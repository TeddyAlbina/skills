## ASP.NET Core Integration

### DI Registration

```csharp
// Minimal setup
builder.Services.AddFido2(options =>
{
    options.RPID = "example.com";
    options.RPName = "My Application";
    options.Origins = new HashSet<string> { "https://example.com" };
});

// From IConfiguration (appsettings.json)
builder.Services.AddFido2(builder.Configuration.GetSection("Fido2"));

// With FIDO Metadata Service (production recommended)
builder.Services.AddFido2(options =>
{
    options.RPID = "example.com";
    options.RPName = "My Application";
    options.Origins = new HashSet<string> { "https://example.com" };
})
.AddFidoMetadataRepository()       // Fetches from mds3.fidoalliance.org
.AddCachedMetadataService();        // Caches via IDistributedCache

// With file system metadata (offline/dev scenarios)
builder.Services.AddFido2(options => { ... })
    .AddCachedMetadataService()
    .AddFileSystemMetadataRepository("/path/to/metadata");

// With custom metadata service
builder.Services.AddFido2(options => { ... })
    .AddMetadataService<MyCustomMetadataService>();
```

### Metadata Service Deep Dive

For complete guidance on implementing custom metadata services and repositories, see [metadata-service-guide.md](metadata-service-guide.md).

### Service Lifetimes

| Service | Lifetime |
|---------|----------|
| `IFido2` / `Fido2` | Scoped |
| `Fido2Configuration` | Singleton |
| `IMetadataService` | Scoped |
| `IMetadataRepository` | Scoped |

### Configuration Properties

```csharp
public class Fido2Configuration
{
    public string RPID { get; set; }                    // Relying Party ID (domain)
    public string RPName { get; set; }                  // Relying Party display name
    public string ServerIcon { get; set; }              // RP icon URL
    public IReadOnlySet<string> Origins { get; set; }   // Allowed origins
    public uint Timeout { get; set; } = 60000;          // Ceremony timeout (ms)
    public int ChallengeSize { get; set; } = 16;        // Challenge bytes
    public int TimestampDriftTolerance { get; set; }    // Clock drift tolerance
    public string MDSCacheDirPath { get; set; }         // MDS cache directory

    // Backup policies: Required, Allowed, Disallowed
    public CredentialBackupPolicy BackupEligibleCredentialPolicy { get; set; } = Allowed;
    public CredentialBackupPolicy BackedUpCredentialPolicy { get; set; } = Allowed;

    // Authenticator statuses that cause rejection
    public AuthenticatorStatus[] UndesiredAuthenticatorMetadataStatuses { get; set; }
}
```

### appsettings.json

```json
{
  "Fido2": {
    "serverDomain": "example.com",
    "origins": [ "https://example.com" ],
    "MDSCacheDirPath": "/tmp/fido2-cache",
    "timestampDriftTolerance": 300,
    "backupEligibleCredentialPolicy": "Allowed",
    "backedUpCredentialPolicy": "Allowed"
  }
}
```


## Complete Sample: ASP.NET Core Controller

### Registration (Attestation) Ceremony

```csharp
using Fido2NetLib;
using Fido2NetLib.Development;
using Fido2NetLib.Objects;
using Microsoft.AspNetCore.Mvc;

[Route("api/[controller]")]
public class Fido2Controller : Controller
{
    private readonly IFido2 _fido2;
    private static readonly DevelopmentInMemoryStore _store = new();

    public Fido2Controller(IFido2 fido2) => _fido2 = fido2;

    // Step 1: Create registration options
    [HttpPost("register/options")]
    public JsonResult RegisterOptions([FromForm] string username, [FromForm] string displayName)
    {
        var user = _store.GetOrAddUser(username, () => new Fido2User
        {
            DisplayName = displayName,
            Name = username,
            Id = System.Text.Encoding.UTF8.GetBytes(username)
        });

        var existingKeys = _store.GetCredentialsByUser(user).Select(c => c.Descriptor).ToList();

        var options = _fido2.RequestNewCredential(new RequestNewCredentialParams
        {
            User = user,
            ExcludeCredentials = existingKeys,
            AuthenticatorSelection = new AuthenticatorSelection
            {
                ResidentKey = ResidentKeyRequirement.Required,
                UserVerification = UserVerificationRequirement.Required
            },
            AttestationPreference = AttestationConveyancePreference.None,
            Extensions = new AuthenticationExtensionsClientInputs
            {
                CredProps = true,
                UserVerificationMethod = true
            }
        });

        HttpContext.Session.SetString("fido2.attestationOptions", options.ToJson());
        return Json(options);
    }

    // Step 2: Verify registration response
    [HttpPost("register/verify")]
    public async Task<JsonResult> RegisterVerify(
        [FromBody] AuthenticatorAttestationRawResponse response, CancellationToken ct)
    {
        var json = HttpContext.Session.GetString("fido2.attestationOptions");
        var options = CredentialCreateOptions.FromJson(json);

        var credential = await _fido2.MakeNewCredentialAsync(new MakeNewCredentialParams
        {
            AttestationResponse = response,
            OriginalOptions = options,
            IsCredentialIdUniqueToUserCallback = static async (args, ct) =>
            {
                var users = await _store.GetUsersByCredentialIdAsync(args.CredentialId, ct);
                return users.Count == 0;
            }
        }, ct);

        _store.AddCredentialToUser(options.User, new StoredCredential
        {
            Id = credential.Id,
            PublicKey = credential.PublicKey,
            UserHandle = credential.User.Id,
            SignCount = credential.SignCount,
            AttestationFormat = credential.AttestationFormat,
            RegDate = DateTimeOffset.UtcNow,
            AaGuid = credential.AaGuid,
            Transports = credential.Transports,
            IsBackupEligible = credential.IsBackupEligible,
            IsBackedUp = credential.IsBackedUp,
            AttestationObject = credential.AttestationObject,
            AttestationClientDataJson = credential.AttestationClientDataJson
        });

        return Json(credential);
    }
}
```

### Authentication (Assertion) Ceremony

```csharp
    // Step 1: Create authentication options
    [HttpPost("auth/options")]
    public ActionResult AuthOptions([FromForm] string username)
    {
        var user = _store.GetUser(username)
            ?? throw new ArgumentException("User not found");

        var existingCredentials = _store.GetCredentialsByUser(user)
            .Select(c => c.Descriptor).ToList();

        var options = _fido2.GetAssertionOptions(new GetAssertionOptionsParams
        {
            AllowedCredentials = existingCredentials,
            UserVerification = UserVerificationRequirement.Preferred,
            Extensions = new AuthenticationExtensionsClientInputs
            {
                UserVerificationMethod = true
            }
        });

        HttpContext.Session.SetString("fido2.assertionOptions", options.ToJson());
        return Json(options);
    }

    // Step 2: Verify authentication response
    [HttpPost("auth/verify")]
    public async Task<JsonResult> AuthVerify(
        [FromBody] AuthenticatorAssertionRawResponse response, CancellationToken ct)
    {
        var json = HttpContext.Session.GetString("fido2.assertionOptions");
        var options = AssertionOptions.FromJson(json);

        var storedCred = _store.GetCredentialById(response.RawId)
            ?? throw new Exception("Unknown credential");

        var result = await _fido2.MakeAssertionAsync(new MakeAssertionParams
        {
            AssertionResponse = response,
            OriginalOptions = options,
            StoredPublicKey = storedCred.PublicKey,
            StoredSignatureCounter = storedCred.SignCount,
            IsUserHandleOwnerOfCredentialIdCallback = static async (args, ct) =>
            {
                var creds = await _store.GetCredentialsByUserHandleAsync(args.UserHandle, ct);
                return creds.Exists(c => c.Descriptor.Id.SequenceEqual(args.CredentialId));
            }
        }, ct);

        _store.UpdateCounter(result.CredentialId, result.SignCount);
        return Json(result);
    }
```

## Usernameless Flow

For usernameless, omit the username in auth options and pass empty allowed credentials:

```csharp
[HttpPost("auth/options")]
public ActionResult AuthOptionsUsernameless()
{
    var options = _fido2.GetAssertionOptions(new GetAssertionOptionsParams
    {
        AllowedCredentials = [],  // Empty = authenticator returns all resident credentials
        UserVerification = UserVerificationRequirement.Required
    });

    HttpContext.Session.SetString("fido2.assertionOptions", options.ToJson());
    return Json(options);
}
```

## Blazor WebAssembly

```csharp
// Client-side Program.cs
builder.Services.AddWebAuthn();

// In a component
@inject WebAuthn WebAuthn

@code {
    async Task Register()
    {
        if (await WebAuthn.IsWebAuthnSupportedAsync())
        {
            var result = await WebAuthn.CreateCredsAsync(options);
            // Send result to server for verification
        }
    }

    async Task Authenticate()
    {
        var result = await WebAuthn.VerifyAsync(assertionOptions);
        // Send result to server for verification
    }
}
```

## Supported Attestation Formats

| Format | Class | Description |
|--------|-------|-------------|
| `none` | `None` | No attestation (most common for web) |
| `packed` | `Packed` | Compact format, self or full attestation |
| `tpm` | `Tpm` | TPM-based attestation |
| `android-key` | `AndroidKey` | Android key attestation |
| `android-safetynet` | `AndroidSafetyNet` | Android SafetyNet (deprecated) |
| `fido-u2f` | `FidoU2f` | U2F backwards compatibility |
| `apple` | `Apple` | Apple platform attestation |
| `apple-appattest` | `AppleAppAttest` | Apple App Attest |

## Supported Algorithms

| COSE Algorithm | Value | Curve/Key |
|----------------|-------|-----------|
| ES256 | -7 | P-256 |
| ES384 | -35 | P-384 |
| ES512 | -36 | P-521 |
| ES256K | -47 | secp256k1 |
| EdDSA | -8 | Ed25519 |
| RS256 | -257 | RSA 2048+ |
| RS384 | -258 | RSA |
| RS512 | -259 | RSA |
| PS256 | -37 | RSA-PSS |
| PS384 | -38 | RSA-PSS |
| PS512 | -39 | RSA-PSS |

## WebAuthn Extensions

```csharp
var extensions = new AuthenticationExtensionsClientInputs
{
    AppID = "https://example.com",           // FIDO U2F backwards compat
    CredProps = true,                         // Credential properties
    UserVerificationMethod = true,            // UV method discovery
    Extensions = true,                        // Generic extension support

    // PRF (Pseudo-Random Function) - for derived secrets
    PRF = new AuthenticationExtensionsPRFInputs { Eval = ... },

    // Large Blob storage
    LargeBlob = new AuthenticationExtensionsLargeBlobInputs
    {
        Support = LargeBlobSupport.Required,  // Registration
        // or Read/Write for authentication
    },

    // Credential Protection
    CredentialProtectionPolicy = CredentialProtectionPolicy.UserVerificationRequired
};
```

## Credential Storage Model

Store these fields per credential for subsequent authentication:

```csharp
public class StoredCredential
{
    public byte[] Id { get; set; }                    // Credential ID
    public byte[] PublicKey { get; set; }             // COSE public key
    public uint SignCount { get; set; }               // Signature counter (cloning detection)
    public AuthenticatorTransport[] Transports { get; set; }
    public bool IsBackupEligible { get; set; }        // BE flag
    public bool IsBackedUp { get; set; }              // BS flag
    public byte[] AttestationObject { get; set; }     // For re-verification
    public byte[] AttestationClientDataJson { get; set; }
    public byte[] UserId { get; set; }                // Owner user ID
    public byte[] UserHandle { get; set; }            // User handle from authenticator
    public string AttestationFormat { get; set; }     // "packed", "tpm", etc.
    public DateTimeOffset RegDate { get; set; }
    public Guid AaGuid { get; set; }                  // Authenticator model ID

    public PublicKeyCredentialDescriptor Descriptor =>
        new(PublicKeyCredentialType.PublicKey, Id, Transports);
}
```

## Error Handling

```csharp
try
{
    var credential = await _fido2.MakeNewCredentialAsync(params, ct);
}
catch (Fido2VerificationException ex)
{
    // ex.Code is Fido2ErrorCode enum (30+ codes)
    // Common codes:
    //   InvalidAttestation, InvalidSignature, InvalidCounter
    //   CredentialIdNotFound, UserNotUnique, BadChallenge
    //   UnsupportedAlgorithm, InvalidAttestationFormat
}
```

## Development Commands

```bash
# Build
dotnet build fido2-net-lib.sln --configuration Release

# Test
dotnet test Tests/Fido2.Tests/Fido2.Tests.csproj

# Test with coverage
dotnet test Tests/Fido2.Tests/Fido2.Tests.csproj --collect:"XPlat Code Coverage"

# Format check
dotnet format --verify-no-changes --no-restore

# Run demo
dotnet run --project Demo/Demo.csproj

# Run Blazor WASM demo
dotnet run --project BlazorWasmDemo/Server/BlazorWasmDemo.Server.csproj
```

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using deprecated `ServerDomain`/`ServerName` | Use `RPID`/`RPName` instead |
| Not storing signature counter | Always persist `SignCount` and pass it to `MakeAssertionAsync` |
| Empty `Origins` set | Must contain at least the origin(s) your app serves from |
| Not caching options server-side | Store `CredentialCreateOptions`/`AssertionOptions` in session/cache between steps |
| Forgetting `AddSession()` | FIDO2 ceremony requires session or equivalent state management |
| Ignoring `IsBackupEligible`/`IsBackedUp` flags | Store and check per your backup policy configuration |
| Not implementing uniqueness callback | `IsCredentialIdUniqueToUserCallback` must query your actual database |
| Using `DevelopmentInMemoryStore` in production | Replace with persistent storage (EF Core, Redis, etc.) |
| Missing HTTPS | WebAuthn requires secure context (HTTPS or localhost) |
| Not calling `AddCachedMetadataService()` | `AddFidoMetadataRepository()` alone does not enable caching |

