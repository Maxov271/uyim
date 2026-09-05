import SwiftUI
import WebKit

/// Uyim.uz — thin native shell around the production website (the same site the
/// Android APK wraps as a TWA). Fixing a layout bug on the site fixes both apps at
/// once since there's no separate iOS-only UI to keep in sync.
private let siteURL = URL(string: "https://uyim.server.umarovgroup.uz/")!

struct WebContainerView: View {
    @State private var isLoading = true
    @State private var loadFailed = false

    var body: some View {
        ZStack {
            WebView(url: siteURL, isLoading: $isLoading, loadFailed: $loadFailed)
                .ignoresSafeArea()

            if isLoading {
                ProgressView()
                    .progressViewStyle(.circular)
                    .tint(Color(red: 0.086, green: 0.196, blue: 0.310)) // --navy
            }

            if loadFailed {
                VStack(spacing: 12) {
                    Image(systemName: "wifi.slash")
                        .font(.system(size: 34))
                        .foregroundStyle(.secondary)
                    Text("Internetga ulanib bo'lmadi")
                        .font(.headline)
                    Text("Ulanishni tekshirib, qayta urinib ko'ring.")
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                }
                .padding(24)
                .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 16))
                .padding(32)
            }
        }
    }
}

/// UIViewRepresentable wrapping WKWebView, with the swipe-back/forward gesture that
/// makes a full-site wrapper actually feel native, and no pinch-zoom (matches the
/// site's own viewport meta, which the WKWebView otherwise wouldn't honor for
/// pinch — WebKit's native pinch gesture is separate from the page's own scale).
struct WebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var loadFailed: Bool

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    func makeUIView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.allowsInlineMediaPlayback = true

        let webView = WKWebView(frame: .zero, configuration: config)
        webView.navigationDelegate = context.coordinator
        webView.allowsBackForwardNavigationGestures = true
        webView.scrollView.pinchGestureRecognizer?.isEnabled = false
        webView.load(URLRequest(url: url))
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKNavigationDelegate {
        let parent: WebView
        init(_ parent: WebView) { self.parent = parent }

        func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
            parent.isLoading = true
            parent.loadFailed = false
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            parent.isLoading = false
        }

        func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
            parent.loadFailed = true
        }

        func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
            parent.isLoading = false
            parent.loadFailed = true
        }

        // Keep everything on the site's own domain inside the app; anything else
        // (tel:, mailto:, t.me deep links to the Telegram app, etc.) hands off to iOS.
        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            guard let url = navigationAction.request.url, let host = url.host else {
                decisionHandler(.allow); return
            }
            if host.hasSuffix("umarovgroup.uz") {
                decisionHandler(.allow)
            } else {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
            }
        }
    }
}
