## Core API

### IFido2 Interface

The main service interface with four methods covering both ceremonies:

```csharp
public interface IFido2
{
    // Registration: Step 1 - Generate options for the client
    CredentialCreateOptions RequestNewCredential(RequestNewCredentialParams params);

    // Registration: Step 2 - Verify the authenticator response
    Task<RegisteredPublicKeyCredential> MakeNewCredentialAsync(MakeNewCredentialParams params, CancellationToken ct = default);

    // Authentication: Step 1 - Generate options for the client
    AssertionOptions GetAssertionOptions(GetAssertionOptionsParams params);

    // Authentication: Step 2 - Verify the authenticator response
    Task<VerifyAssertionResult> MakeAssertionAsync(MakeAssertionParams params, CancellationToken ct = default);
}
```

### Key Types

| Type | Namespace | Purpose |
|------|-----------|---------|
| `Fido2Configuration` | `Fido2NetLib` | RP config: RPID, RPName, Origins, Timeout, ChallengeSize |
| `Fido2User` | `Fido2NetLib` | User entity: Name, DisplayName, Id (byte[]) |
| `CredentialCreateOptions` | `Fido2NetLib` | Registration options sent to client |
| `AssertionOptions` | `Fido2NetLib` | Authentication options sent to client |
| `AuthenticatorAttestationRawResponse` | `Fido2NetLib` | Raw JSON from client during registration |
| `AuthenticatorAssertionRawResponse` | `Fido2NetLib` | Raw JSON from client during authentication |
| `RegisteredPublicKeyCredential` | `Fido2NetLib.Objects` | Output of successful registration |
| `VerifyAssertionResult` | `Fido2NetLib.Objects` | Output of successful authentication |
| `AuthenticatorSelection` | `Fido2NetLib.Objects` | Authenticator criteria (attachment, UV, RK) |
| `PublicKeyCredentialDescriptor` | `Fido2NetLib.Objects` | Credential reference (type, id, transports) |
| `AuthenticationExtensionsClientInputs` | `Fido2NetLib.Objects` | Extension inputs (PRF, LargeBlob, CredProps, AppID) |
| `CredentialPublicKey` | `Fido2NetLib.Objects` | COSE key with Verify() method |
| `AuthenticatorData` | `Fido2NetLib.Objects` | Parsed authenticator data |

### Parameter Objects

```csharp
// Registration request
public sealed class RequestNewCredentialParams
{
    public required Fido2User User { get; init; }
    public IReadOnlyList<PublicKeyCredentialDescriptor> ExcludeCredentials { get; init; } = [];
    public AuthenticatorSelection AuthenticatorSelection { get; init; } = AuthenticatorSelection.Default;
    public AttestationConveyancePreference AttestationPreference { get; init; } = AttestationConveyancePreference.None;
    public AuthenticationExtensionsClientInputs? Extensions { get; init; }
    public IReadOnlyList<PubKeyCredParam> PubKeyCredParams { get; init; } = PubKeyCredParam.Defaults;
}

// Registration verification
public sealed class MakeNewCredentialParams
{
    public required AuthenticatorAttestationRawResponse AttestationResponse { get; init; }
    public required CredentialCreateOptions OriginalOptions { get; init; }
    public required IsCredentialIdUniqueToUserAsyncDelegate IsCredentialIdUniqueToUserCallback { get; init; }
}

// Authentication request
public sealed class GetAssertionOptionsParams
{
    public IReadOnlyList<PublicKeyCredentialDescriptor> AllowedCredentials { get; init; } = [];
    public UserVerificationRequirement? UserVerification { get; init; }
    public AuthenticationExtensionsClientInputs? Extensions { get; init; }
}

// Authentication verification
public sealed class MakeAssertionParams
{
    public required AuthenticatorAssertionRawResponse AssertionResponse { get; init; }
    public required AssertionOptions OriginalOptions { get; init; }
    public required byte[] StoredPublicKey { get; init; }
    public required uint StoredSignatureCounter { get; init; }
    public required IsUserHandleOwnerOfCredentialIdAsync IsUserHandleOwnerOfCredentialIdCallback { get; init; }
}
```

### Callback Delegates

```csharp
// Registration: verify credential ID is unique to user
public delegate Task<bool> IsCredentialIdUniqueToUserAsyncDelegate(
    IsCredentialIdUniqueToUserParams args, CancellationToken ct);

// Authentication: verify user handle owns the credential
public delegate Task<bool> IsUserHandleOwnerOfCredentialIdAsync(
    IsUserHandleOwnerOfCredentialIdParams args, CancellationToken ct);
```