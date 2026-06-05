# Manual Certificate Installation Guide

## Certificate Location

The certificate file has been opened in Explorer:
```
C:\Users\Sails\.mitmproxy\mitmproxy-ca-cert.p12
```

## Installation Steps

### Method 1: Double-click Installation

1. **Double-click** `mitmproxy-ca-cert.p12`
2. **Store Location**: Current User
3. Click "Next"
4. **Password**: (leave empty, just click Next)
5. **Certificate Store**: 
   - Select "Place all certificates in the following store"
   - Click "Browse"
   - Select "Trusted Root Certification Authorities"
6. Click "Next" → "Finish"
7. Click "Yes" on security warning

### Method 2: Using certmgr.msc

1. Press `Win + R`
2. Type: `certmgr.msc`
3. Right-click "Trusted Root Certification Authorities"
4. Select "All Tasks" → "Import"
5. Browse to: `C:\Users\Sails\.mitmproxy\mitmproxy-ca-cert.p12`
6. Password: (leave empty)
7. Finish

### Method 3: PowerShell (Run as Admin)

```powershell
$cert = Get-PfxCertificate -FilePath "$env:USERPROFILE\.mitmproxy\mitmproxy-ca-cert.p12"
Import-Certificate -FilePath "$env:USERPROFILE\.mitmproxy\mitmproxy-ca-cert.cer" -CertStoreLocation Cert:\CurrentUser\Root
```

## Verify Installation

After installation, verify:

1. Press `Win + R`
2. Type: `certmgr.msc`
3. Go to: Trusted Root Certification Authorities → Certificates
4. Look for: "mitmproxy"

## Current Status

- ✅ mitmproxy running on 127.0.0.1:8080
- ✅ Certificate generated
- ⏳ Certificate installation (in progress)
- ⏳ Proxifier configuration
- ⏳ Test with MiniWorld

---

**Next**: After installing certificate, configure Proxifier to use 127.0.0.1:8080
