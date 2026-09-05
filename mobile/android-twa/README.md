# Uyim — Android TWA wrapper

A [Trusted Web Activity](https://developer.chrome.com/docs/android/trusted-web-activity/)
around the live site (`https://uyim.server.umarovgroup.uz`), built via
[PWABuilder](https://www.pwabuilder.com/)'s cloud API — no local Android SDK/Studio
needed to produce a build. Package id: `uz.uyim.twa`.

Signed builds and the Play-Store bundle live in `builds/` and the signing keystore in
`keystore/` — **both are git-ignored** (see repo root `.gitignore`) and only exist on
this machine. Download builds from the repo's
[Releases](https://github.com/Maxov271/uyim/releases) page instead; get the keystore
from whoever last built it if you need to publish an update under the same app
identity.

## Why this matters: reuse the keystore

Google Play (and the Digital Asset Links check that makes the TWA render full-screen
instead of falling back to a browser URL bar) requires every update to be **signed
with the exact same key**. `keystore/signing.keystore` is that key for the current
(v2) build — `keystore/signing-key-info.txt` has its password/alias. Any future
rebuild should pass this same keystore back into PWABuilder (`signingMode: "mine"`
with the keystore base64-encoded in the request) instead of `signingMode: "new"`,
which mints a fresh one every time. `keystore/signing-v1.keystore` /
`signing-key-info-v1.txt` are kept only for reference — v1 was superseded once real
device testing surfaced the layout bugs fixed in the `d7c1978`/`5964fd5` commits.

`frontend/.well-known/assetlinks.json` lists both v1 and v2 certificate fingerprints
so either test build still verifies; once you settle on one keystore going forward,
you can drop the old fingerprint.

## Rebuilding

The request this repo's builds were generated from called
`POST https://pwabuilder-cloudapk.azurewebsites.net/generateAppPackage` with the site's
manifest URL, package id, and a signing block. To reuse the existing key, read
`keystore/signing.keystore` as base64 and set `signingMode: "mine"` with that content
plus the password/alias from `signing-key-info.txt` in the request body — see
[PWABuilder's docs](https://docs.pwabuilder.com/) for the full request shape.
