# p3u - Python 3 Uploader

## Purpose
I needed a flexible and simple file upload and download tool with SSL support for local use at customer site during penetration tests.
So I stumbled over the gist files already implementing it and modified them for my needs.

Feel free to contribute with PRs.

## Usage
Use the following arguments: \
`p3u.py -l ip -p port -a user:password -c server.pem`

Generate your cert with \
`openssl req -new -x509 -keyout server.pem -out server.pem -days 365 -nodes -subj "/C=/ST=/O=/OU=/CN="`

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
ssh -nNT -4 -R 5555:localhost:80 h8 -v
```
4. Run p3u.py

This will handle and offload SSL connections on the server with certbot or similar without the need to run the challenge locally.

## Credits
UniIsland \
4d4c
