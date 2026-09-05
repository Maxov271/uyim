# Uyim — iOS shell (WKWebView wrapper)

A minimal SwiftUI + WKWebView app that loads the production site
(`https://uyim.server.umarovgroup.uz`) full-screen, native chrome (swipe back/forward,
no pinch-zoom, an offline error state). It's the iOS equivalent of the Android APK's
TWA wrapper — same idea, same site, so a layout fix on the site fixes both at once.

This is **not** the `../` Expo/React Native skeleton (that's a separate, unstarted,
fully-native rewrite per `../../docs/MOBILE_APP_PLAN.md`). This is the fast path to a
real, installable iPhone app today.

## Run it yourself

Needs a Mac with Xcode. `Uyim.xcodeproj` is committed and ready to open —

```bash
cd mobile/ios-webview
open Uyim.xcodeproj
```

It's generated from `project.yml` via [XcodeGen](https://github.com/yonaskolb/XcodeGen)
(`brew install xcodegen`) — only re-run `xcodegen generate` if you change `project.yml`
(new source files, icon, bundle id, etc.).

**Simulator** (no Apple ID needed): pick any iPhone simulator as the run destination and
hit ▶ in Xcode, or from the terminal:

```bash
xcodebuild -project Uyim.xcodeproj -scheme Uyim -sdk iphonesimulator -derivedDataPath build build
xcrun simctl boot "iPhone 17 Pro"
xcrun simctl install "iPhone 17 Pro" build/Build/Products/Debug-iphonesimulator/Uyim.app
xcrun simctl launch "iPhone 17 Pro" uz.uyim.app
```

**Real iPhone**: connect it, select it as the run destination in Xcode, then
Signing & Capabilities → pick your own Apple ID as the team (a free personal account
works — Xcode will offer to create one). Hit ▶. The app runs for 7 days before Xcode
needs to re-sign it (normal for a free account); a paid Apple Developer Program
membership removes that limit and enables TestFlight.

## Files

- `project.yml` — XcodeGen spec (target, bundle id `uz.uyim.app`, Info.plist, icon)
- `UyimApp/UyimApp.swift` — app entry point
- `UyimApp/WebContainerView.swift` — the WKWebView wrapper (loading/offline states,
  swipe navigation, keeps `*.umarovgroup.uz` links in-app and hands off everything
  else — `tel:`, `t.me/...` — to iOS)
- `UyimApp/Assets.xcassets/AppIcon.appiconset/` — icons generated from
  `../../frontend/assets/icons/icon-512.png`
