import XCTest
@testable import MewsAndWoofs

final class MewsAndWoofsTests: XCTestCase {
    func testControlledInputProducesStableResponse() {
        let input = ResponseInput(
            context: .playtime,
            mediaKind: .video,
            loudness: .moderate,
            activity: .active,
            seed: 42
        )

        XCTAssertEqual(ResponseLibrary.select(for: input), ResponseLibrary.select(for: input))
    }

    func testEveryContextHasEligibleContent() {
        for context in MomentContext.allCases {
            let response = ResponseLibrary.select(
                for: ResponseInput(
                    context: context,
                    mediaKind: .video,
                    loudness: .moderate,
                    activity: .active,
                    seed: 7
                )
            )
            XCTAssertTrue(response.contexts.contains(context), "Missing content for \(context)")
        }
    }

    func testContentIdentifiersAreUniqueAndIndependentOfText() {
        let ids = ResponseLibrary.responses.map(\.id)
        XCTAssertEqual(Set(ids).count, ids.count)
        XCTAssertTrue(ids.allSatisfy { !$0.contains(" ") })
    }

    func testBubbleMovementStaysInsideSafeBounds() {
        var layout = BubbleLayout.initial
        layout.move(horizontal: 10, vertical: -10)
        XCTAssertEqual(layout.x, 0.67, accuracy: 0.0001)
        XCTAssertEqual(layout.y, 0.16, accuracy: 0.0001)

        layout.move(horizontal: -10, vertical: 10)
        XCTAssertEqual(layout.x, 0.33, accuracy: 0.0001)
        XCTAssertEqual(layout.y, 0.84, accuracy: 0.0001)
    }

    func testBubbleScaleAndResetAreBounded() {
        var layout = BubbleLayout.initial
        layout.move(horizontal: 10, vertical: 10)
        layout.resize(by: 10)
        XCTAssertEqual(layout.scale, 1.28)
        XCTAssertEqual(layout.x, 0.5776, accuracy: 0.0001)
        XCTAssertEqual(layout.y, 0.7952, accuracy: 0.0001)
        layout.resize(to: -10)
        XCTAssertEqual(layout.scale, 0.72)
        layout.reset()
        XCTAssertEqual(layout, .initial)
    }

    func testSelectingContextRecomputesResponseFromStableInput() {
        var first = CreationDraft.demo()
        var second = CreationDraft.demo()
        first.selectContext(.foodNearby)
        second.selectContext(.foodNearby)

        XCTAssertEqual(first.response.id, second.response.id)
        XCTAssertTrue(first.response.contexts.contains(.foodNearby))
    }
}
