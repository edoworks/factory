import CoreGraphics
import Foundation

enum MomentContext: String, CaseIterable, Identifiable, Codable {
    case greeting
    case foodNearby
    case playtime
    case doorOrWindow
    case notSure

    var id: String { rawValue }

    var title: String {
        switch self {
        case .greeting: "Saying hello"
        case .foodNearby: "Food nearby"
        case .playtime: "Playtime"
        case .doorOrWindow: "Door or window"
        case .notSure: "Not sure"
        }
    }

    var symbol: String {
        switch self {
        case .greeting: "hand.wave.fill"
        case .foodNearby: "fork.knife"
        case .playtime: "tennisball.fill"
        case .doorOrWindow: "door.left.hand.open"
        case .notSure: "sparkles"
        }
    }
}

enum MediaKind: String, Codable {
    case video
    case audio
}

enum LoudnessBand: String, Codable {
    case quiet
    case moderate
    case loud
}

enum ActivityBand: String, Codable {
    case sparse
    case active
}

struct ResponseInput: Equatable {
    let context: MomentContext?
    let mediaKind: MediaKind
    let loudness: LoudnessBand
    let activity: ActivityBand
    let seed: UInt64
}

struct PetResponse: Identifiable, Equatable {
    let id: String
    let contexts: Set<MomentContext>
    let activity: Set<ActivityBand>
    let text: String
    let accessibilityText: String
}

enum ResponseLibrary {
    static let responses: [PetResponse] = [
        PetResponse(
            id: "hello-inspection",
            contexts: [.greeting, .notSure],
            activity: [.sparse, .active],
            text: "Hello. I have inspected the room. You may continue.",
            accessibilityText: "Imagined response: Hello. I have inspected the room. You may continue."
        ),
        PetResponse(
            id: "hello-schedule",
            contexts: [.greeting],
            activity: [.active],
            text: "You're late. I scheduled this hello three naps ago.",
            accessibilityText: "Imagined response: You're late. I scheduled this hello three naps ago."
        ),
        PetResponse(
            id: "food-meeting",
            contexts: [.foodNearby],
            activity: [.sparse, .active],
            text: "This meeting could have been a treat.",
            accessibilityText: "Imagined response: This meeting could have been a treat."
        ),
        PetResponse(
            id: "food-cabinet",
            contexts: [.foodNearby, .notSure],
            activity: [.active],
            text: "I heard the snack cabinet think about me.",
            accessibilityText: "Imagined response: I heard the snack cabinet think about me."
        ),
        PetResponse(
            id: "play-chaos",
            contexts: [.playtime],
            activity: [.active],
            text: "I reviewed the toy. It needs more chaos.",
            accessibilityText: "Imagined response: I reviewed the toy. It needs more chaos."
        ),
        PetResponse(
            id: "play-rematch",
            contexts: [.playtime],
            activity: [.sparse, .active],
            text: "A rematch? Brave of you to ask.",
            accessibilityText: "Imagined response: A rematch? Brave of you to ask."
        ),
        PetResponse(
            id: "door-management",
            contexts: [.doorOrWindow],
            activity: [.sparse, .active],
            text: "Open it? No. I just enjoy management.",
            accessibilityText: "Imagined response: Open it? No. I just enjoy management."
        ),
        PetResponse(
            id: "door-weather",
            contexts: [.doorOrWindow],
            activity: [.active],
            text: "The weather is doing something without my permission.",
            accessibilityText: "Imagined response: The weather is doing something without my permission."
        ),
        PetResponse(
            id: "mystery-announcement",
            contexts: [.notSure],
            activity: [.sparse, .active],
            text: "I have an announcement. Details are classified.",
            accessibilityText: "Imagined response: I have an announcement. Details are classified."
        ),
        PetResponse(
            id: "mystery-acoustics",
            contexts: [.notSure, .greeting],
            activity: [.active],
            text: "No request. I was testing the acoustics.",
            accessibilityText: "Imagined response: No request. I was testing the acoustics."
        ),
        PetResponse(
            id: "quiet-footnote",
            contexts: Set(MomentContext.allCases),
            activity: [.sparse],
            text: "That was the short version. The footnotes are also me.",
            accessibilityText: "Imagined response: That was the short version. The footnotes are also me."
        ),
        PetResponse(
            id: "active-important",
            contexts: Set(MomentContext.allCases),
            activity: [.active],
            text: "Important update: I remain extremely interesting.",
            accessibilityText: "Imagined response: Important update: I remain extremely interesting."
        )
    ]

    static func select(for input: ResponseInput) -> PetResponse {
        let context = input.context ?? .notSure
        let eligible = responses.filter {
            $0.contexts.contains(context) && $0.activity.contains(input.activity)
        }
        let candidates = eligible.isEmpty ? responses : eligible
        let key = [
            context.rawValue,
            input.mediaKind.rawValue,
            input.loudness.rawValue,
            input.activity.rawValue,
            String(input.seed),
        ].joined(separator: "|")
        return candidates[Int(stableHash(key) % UInt64(candidates.count))]
    }

    private static func stableHash(_ value: String) -> UInt64 {
        value.utf8.reduce(14_695_981_039_346_656_037) { hash, byte in
            (hash ^ UInt64(byte)) &* 1_099_511_628_211
        }
    }
}

struct BubbleLayout: Equatable {
    static let initial = BubbleLayout(x: 0.5, y: 0.27, scale: 1)

    var x: CGFloat
    var y: CGFloat
    var scale: CGFloat

    mutating func move(horizontal: CGFloat, vertical: CGFloat) {
        x += horizontal
        y += vertical
        clampPosition()
    }

    mutating func resize(by delta: CGFloat) {
        resize(to: scale + delta)
    }

    mutating func resize(to newScale: CGFloat) {
        scale = min(max(newScale, 0.72), 1.28)
        clampPosition()
    }

    mutating func reset() {
        self = .initial
    }

    private mutating func clampPosition() {
        // The bubble occupies at most 66% by 32% of the smallest canvas.
        let horizontalInset = 0.33 * scale
        let verticalInset = 0.16 * scale
        x = min(max(x, horizontalInset), 1 - horizontalInset)
        y = min(max(y, verticalInset), 1 - verticalInset)
    }
}

struct CreationDraft: Equatable {
    var context: MomentContext?
    var bubble = BubbleLayout.initial
    var response: PetResponse

    static func demo(context: MomentContext? = nil) -> CreationDraft {
        let input = ResponseInput(
            context: context,
            mediaKind: .video,
            loudness: .moderate,
            activity: .active,
            seed: 42
        )
        return CreationDraft(
            context: context,
            response: ResponseLibrary.select(for: input)
        )
    }

    mutating func selectContext(_ newContext: MomentContext?) {
        context = newContext
        response = ResponseLibrary.select(
            for: ResponseInput(
                context: newContext,
                mediaKind: .video,
                loudness: .moderate,
                activity: .active,
                seed: 42
            )
        )
    }
}
