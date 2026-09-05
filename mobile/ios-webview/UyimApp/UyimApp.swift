import SwiftUI

@main
struct UyimApp: App {
    var body: some Scene {
        WindowGroup {
            WebContainerView()
                .ignoresSafeArea(edges: .bottom)
        }
    }
}
