## Architecture

**Dependency graph:**
```
Fido2.Models
    ^
  Fido2  (depends on: NSec.Cryptography, System.Formats.Cbor, Microsoft.IdentityModel.JsonWebTokens)
    ^
    +-- Fido2.AspNet      (+ Microsoft.AspNetCore.App framework ref)
    +-- Fido2.Ctap2
    +-- Fido2.Development

Fido2.BlazorWebAssembly (depends on: Fido2.Models, Microsoft.AspNetCore.Components.Web)
```