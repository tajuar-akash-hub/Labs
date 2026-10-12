# Understanding Domain Names, DNS, VPS, HTTP/HTTPS, and WWW

**Level:** Beginner  
**Topic:** Web infrastructure and networking  
**Goal:** Understand how a website becomes accessible through a human-readable domain name.

---

## 1. Introduction

Suppose you build an AI application using FastAPI and deploy it on a VPS. Your application works, but users must access it through an IP address such as `203.0.113.10`.

You want users to access it using a memorable address:

`https://myaiapp.com`

How does that work? Who provides the domain? How does the domain find your server? Why do some websites use `www`? And what is the difference between HTTP and HTTPS?

This note explains the complete process.

## 2. What Is a VPS?

**Definition:** A Virtual Private Server (VPS) is a virtual machine running on a physical server. It has allocated resources such as CPU, RAM, storage, and networking.

Think of a VPS as a computer rented from a cloud or hosting provider. You can install software, deploy applications, configure a web server, and run services.

Examples of VPS providers include AWS EC2, DigitalOcean, and Hetzner.

A typical deployment looks like this:

```text
Your Computer
     |
     | SSH
     v
    VPS
     |
     +-- Linux
     +-- Nginx
     +-- FastAPI
     +-- Application files
```

A VPS can have a public IP address that allows users to connect to services running on it, provided networking and firewall rules permit those connections.

## 3. What Is an IP Address?

**Definition:** An IP address identifies a network interface so that devices can communicate using the Internet Protocol.

There are two important IPv4 address categories.

### Private IP address

Private addresses are used inside private networks. They are not directly routable across the public internet.

Common private IPv4 ranges are:

- `10.0.0.0/8`
- `172.16.0.0/12`
- `192.168.0.0/16`

For example, `10.250.10.201` is a private IP address.

### Public IP address

A public IP address can be globally routed, although firewalls, routing rules, and provider configurations determine whether incoming connections actually reach your server.

For example, a VPS provider may assign a public IPv4 address to your VPS.

**Important:** A public IP observed by an outgoing connection does not necessarily mean that the same IP accepts incoming connections to your application.

## 4. What Is a Domain Name?

**Definition:** A domain name is a human-readable name registered within the domain name system.

For example:

- `myaiapp.com`
- `example.org`
- `mycompany.net`

People use domain names because they are easier to remember than numerical IP addresses.

Think of the relationship like this:

```text
Human-readable name: myaiapp.com
                 |
                 v
             DNS lookup
                 |
                 v
       Relevant destination IP
                 |
                 v
           Your web server
```

DNS does not carry all the website traffic. It helps the browser discover where to connect.

## 5. Who Sells Domain Names?

Three roles are important.

### 5.1 Domain registrar

A registrar lets you register a domain name, manage its registration, and renew it.

Examples include Namecheap, Porkbun, and Cloudflare Registrar.

You generally provide account and contact information, choose an available name, and pay the registration fee.

For an ordinary `.com` domain, you generally do not need to submit your application code or VPS configuration.

### 5.2 Domain registry

A registry maintains the authoritative database for a top-level domain.

For example, the `.com` registry maintains registration information for `.com` domains.

### 5.3 DNS provider

A DNS provider hosts DNS records that help direct queries for your domain to the appropriate destination.

A registrar and DNS provider can be the same company, but they do not have to be.

**Remember:** Domain registration gives you the right to use a name for a specified period. It does not purchase a server or guarantee website availability.

## 6. What Is DNS?

**DNS stands for Domain Name System.**

It is a distributed naming system that helps computers find information associated with domain names.

Suppose your domain is `myaiapp.com` and your VPS has a public IP address.

You can create a DNS record that associates the domain with that address.

### Common DNS records

| Record | Purpose | Example |
|---|---|---|
| A | Maps a hostname to an IPv4 address | `myaiapp.com → 203.0.113.10` |
| AAAA | Maps a hostname to an IPv6 address | `myaiapp.com → IPv6 address` |
| CNAME | Makes one hostname an alias of another | `www → myaiapp.com` |
| MX | Specifies mail servers for a domain | Email delivery |
| TXT | Stores text used for verification and other purposes | Domain ownership verification |

The IP address `203.0.113.10` above is reserved for documentation. It is an example, not a usable production server address.

### How a DNS lookup works

```text
1. User enters myaiapp.com
              |
              v
2. Browser/OS checks available cached information
              |
              v
3. DNS resolver obtains the required DNS answer
              |
              v
4. Browser receives the destination IP
              |
              v
5. Browser connects to the web server
              |
              v
6. Website response returns to the browser
```

The resolver may already have the answer cached, so every lookup does not require a complete DNS resolution process.

## 7. How to Connect a Domain to a VPS

Assume you own `myaiapp.com` and your VPS has a dedicated public IPv4 address.

### Step 1: Register the domain

Choose a registrar and register an available domain.

### Step 2: Configure DNS

Open the DNS management panel and create records similar to these:

| Type | Name | Value |
|---|---|---|
| A | `@` | Your VPS public IPv4 address |
| CNAME | `www` | `myaiapp.com` |

The `@` symbol typically represents the root domain.

The CNAME example assumes your DNS provider supports this configuration and that the target is configured appropriately.

### Step 3: Configure your VPS

Install a web server such as Nginx.

Configure Nginx to accept requests for your domain and forward them to your application.

For example, a FastAPI application might listen on `127.0.0.1:8000`, while Nginx accepts public web requests.

### Step 4: Configure the firewall

Allow the necessary inbound traffic:

- TCP port `80` for HTTP.
- TCP port `443` for HTTPS.

The exact configuration depends on your VPS provider, operating system, and firewall.

### Step 5: Configure HTTPS

Obtain a TLS certificate for your domain. Let's Encrypt is one common certificate authority.

Configure Nginx or your hosting platform to serve HTTPS.

### Step 6: Test the website

Open:

`https://myaiapp.com`

If DNS, routing, the firewall, the web server, and the application are configured correctly, the browser should display your website.

## 8. What Is HTTP?

**HTTP stands for Hypertext Transfer Protocol.**

It defines how clients, such as browsers, exchange requests and responses with web servers.

For example, a browser may request:

```http
GET / HTTP/1.1
Host: myaiapp.com
```

The server processes the request and returns a response containing a status code, headers, and potentially a response body.

Ordinary HTTP does not encrypt the application data in transit.

HTTP normally uses TCP port `80`.

## 9. What Is HTTPS?

**HTTPS is HTTP protected by TLS (Transport Layer Security).**

TLS provides encryption, integrity protection, and authentication of the server through its certificate.

HTTPS normally uses TCP port `443`. HTTP/3 uses QUIC over UDP, normally on port `443`.

For example:

```text
http://myaiapp.com
https://myaiapp.com
```

The first URL uses ordinary HTTP. The second uses HTTP over TLS.

For public production websites, HTTPS is the standard choice.

### How HTTPS works

```text
Browser
   |
   | 1. Requests HTTPS connection
   v
TLS handshake
   |
   | 2. Verifies certificate and establishes keys
   v
Encrypted HTTP communication
   |
   | 3. Sends requests and receives responses
   v
Web server
```

HTTPS protects data in transit, but it does not guarantee that a website is trustworthy or that its server is secure against every attack.

## 10. What Is WWW?

`www` stands for **World Wide Web**.

Historically, organizations often used different hostnames for different services:

- `www.example.com` — website
- `mail.example.com` — mail service
- `ftp.example.com` — file transfer service

Today, `www` is optional. It is simply a subdomain label.

Consider these addresses:

```text
https://example.com
https://www.example.com
https://api.example.com
```

Their components are:

- `https://` — the protocol scheme.
- `www` — a subdomain label.
- `example.com` — the registered domain.
- `api` — another possible subdomain label.

The DNS configuration and web server determine where each hostname leads.

### Why do both www and non-www addresses work?

The owner can configure both hostnames to reach the same service.

For example:

```text
example.com
     |
     v
DNS A record
     |
     v
VPS public IP

www.example.com
     |
     v
DNS CNAME
     |
     v
example.com
```

The web server and TLS certificate must also support the requested hostname.

One hostname can redirect to the other, creating a single preferred address.

For a personal project, you can use `example.com` as the main address and redirect `www.example.com` to it.

## 11. Why Did the Railway Preview URL Work?

During the experiment, the Railway VM returned these addresses:

```text
10.250.10.201
10.168.214.184
fd12:bdce:dfa9:1:9000:57:b228:d6b8
```

The two IPv4 addresses are private addresses. The IPv6 address is a unique-local address, not a globally routable public address.

You then ran:

```bash
curl -4 https://icanhazip.com
```

It returned:

```text
208.77.246.95
```

This result showed the public IPv4 address observed by the external service for that outgoing connection. It did not establish that the address was dedicated to your VM or could receive inbound web traffic.

When you tried opening the IP directly in a browser, the connection timed out.

However, your Railway preview URL worked:

`https://preview-4a7df0614099a6cd.up.railway.app`

This is possible because Railway provides public routing infrastructure. It accepts requests for the preview hostname and routes them to the appropriate application.

The architecture is conceptually similar to:

```text
Visitor's browser
        |
        v
Railway public hostname
        |
        v
Railway public gateway
        |
        v
Your VM and application
```

The public gateway acts as the entry point. The VM does not need its own directly accessible public IP for this arrangement.

**Lesson:** A working public website does not prove that its underlying VM has a directly reachable public IP address.

## 12. Why Do People Buy Domains?

People register domains for several reasons:

1. **Memorability:** `myaiapp.com` is easier to remember than a long generated URL.
2. **Branding:** A domain gives a project or business a recognizable identity.
3. **Professional email:** You can configure addresses such as `support@myaiapp.com` with an email provider.
4. **Hosting flexibility:** You can change hosting providers while keeping the same domain.
5. **Subdomains:** You can organize different services under one domain.

For example:

```text
myaiapp.com       -> Frontend website
api.myaiapp.com   -> Backend API
docs.myaiapp.com  -> Documentation
```

A domain does not automatically provide hosting, email service, HTTPS, or better search rankings. Those require separate services or configurations.

## 13. Is a Domain Permanent?

No. A domain is registered for a defined period, commonly one year at a time, and must be renewed.

A VPS also requires an active hosting arrangement.

To maintain a website long-term:

- Renew the domain registration.
- Keep the VPS active and paid for.
- Configure automatic application restarts.
- Maintain firewall rules and software updates.
- Renew or automatically manage TLS certificates.
- Back up important data.
- Monitor availability and resource usage.

A domain and a VPS are separate resources. Renewing one does not automatically renew the other.

## 14. Practical Commands

These commands help inspect your networking environment.

### Display assigned IP addresses

```bash
hostname -I
```

Shows IP addresses assigned to the current machine. Some may be private or internal addresses.

### Check the public IPv4 observed for outgoing traffic

```bash
curl -4 https://icanhazip.com
```

This reports the address seen by that external service. It does not guarantee inbound reachability.

### Check the DNS answer for a domain

```bash
dig myaiapp.com A
dig www.myaiapp.com A
```

Install the appropriate DNS utilities package if `dig` is unavailable.

### Check whether an HTTP service responds

```bash
curl -I http://myaiapp.com
curl -I https://myaiapp.com
```

These commands display response headers if a connection succeeds. A failure may result from DNS, networking, TLS, or server configuration.

### Check whether a port is listening on Linux

```bash
ss -lntp
```

This lists listening TCP sockets. It can help verify whether your application or web server is listening on the expected port.

## 15. Common Misconceptions

**Misconception 1:** Buying a domain gives you a server.

Correction: A domain is a registered name. Hosting provides the computing environment.

**Misconception 2:** DNS carries every website request.

Correction: DNS helps locate the destination. The browser normally connects to the web server for HTTP communication.

**Misconception 3:** Every public IP can host a website.

Correction: The IP must route to the intended server, and the appropriate port and service must be reachable.

**Misconception 4:** HTTPS and `www` are alternatives.

Correction: HTTPS is a protocol scheme. `www` is a hostname label. You can use them together.

**Misconception 5:** A working domain means the application will stay online forever.

Correction: The domain, DNS, hosting, application, network, and certificate lifecycle must all be maintained.

## 16. Final Summary

The complete relationship is:

```text
Domain registrar
      |
      | Registers a domain
      v
Domain name
      |
      | DNS resolves the hostname
      v
Destination IP / public gateway
      |
      | Network connection
      v
Web server or reverse proxy
      |
      | Forwards the request
      v
Application
      |
      | Returns a response
      v
Browser displays the website
```

Remember these distinctions:

- **Domain:** The human-readable name.
- **Registrar:** The service through which you register that name.
- **DNS:** The system that provides information about the domain's destination.
- **IP address:** A network address used to communicate with a destination.
- **VPS:** The virtual computer that runs your application.
- **HTTP:** The protocol for web requests and responses.
- **HTTPS:** HTTP protected by TLS.
- **WWW:** An optional subdomain label.

Once you understand these components, you can reason about how websites are published, how requests reach servers, and why a domain can continue pointing to a new server even when the hosting infrastructure changes.
