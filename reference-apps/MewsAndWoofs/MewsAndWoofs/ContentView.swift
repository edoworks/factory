import SwiftUI

private enum AppScreen {
    case welcome
    case editor
    case preview
}

struct ContentView: View {
    @Environment(\.horizontalSizeClass) private var horizontalSizeClass
    @Environment(\.accessibilityReduceMotion) private var reduceMotion
    @State private var screen: AppScreen
    @State private var draft = CreationDraft.demo()

    init() {
        let arguments = ProcessInfo.processInfo.arguments
        if arguments.contains("-UITestPreview") {
            _screen = State(initialValue: .preview)
        } else if arguments.contains("-UITestDemoEditor") {
            _screen = State(initialValue: .editor)
        } else {
            _screen = State(initialValue: .welcome)
        }
    }

    var body: some View {
        ZStack {
            MWPalette.cream.ignoresSafeArea()

            switch screen {
            case .welcome:
                WelcomeView(onTryDemo: { screen = .editor })
                    .transition(.opacity.combined(with: .scale(scale: 0.98)))
            case .editor:
                editor
                    .transition(.opacity)
            case .preview:
                PreviewView(
                    draft: draft,
                    onEdit: { screen = .editor },
                    onFinish: {
                        draft = .demo()
                        screen = .welcome
                    }
                )
                .transition(.opacity)
            }
        }
        .tint(MWPalette.coral)
        .animation(reduceMotion ? nil : .snappy(duration: 0.28), value: screen)
    }

    @ViewBuilder
    private var editor: some View {
        if horizontalSizeClass == .regular {
            HStack(spacing: 0) {
                canvasColumn
                    .frame(maxWidth: .infinity)
                Divider()
                    .overlay(MWPalette.navy.opacity(0.12))
                controls
                    .frame(width: 390)
            }
            .padding(.horizontal, 30)
            .padding(.vertical, 24)
            .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
        } else {
            ScrollView {
                VStack(spacing: 20) {
                    canvasColumn
                    controls
                }
                .padding(.horizontal, 18)
                .padding(.vertical, 14)
            }
        }
    }

    private var canvasColumn: some View {
        VStack(alignment: .leading, spacing: 12) {
            Group {
                if horizontalSizeClass == .regular {
                    HStack(alignment: .firstTextBaseline) {
                        editorTitle
                        Spacer()
                        entertainmentLabel
                    }
                } else {
                    VStack(alignment: .leading, spacing: 7) {
                        editorTitle
                        entertainmentLabel
                    }
                }
            }

            MomentCanvas(draft: $draft, isPreview: false)
                .frame(maxWidth: horizontalSizeClass == .regular ? 520 : 430)
                .frame(maxWidth: .infinity)
                .accessibilityIdentifier("momentCanvas")
        }
    }

    private var editorTitle: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text("MAKE THE MOMENT YOURS")
                .font(.caption.weight(.black))
                .tracking(1.4)
                .foregroundStyle(MWPalette.coral)
            Text("One tiny sound. One big little thought.")
                .font(.title2.weight(.bold))
                .foregroundStyle(MWPalette.navy)
        }
    }

    private var entertainmentLabel: some View {
        Label("Imagined for fun", systemImage: "sparkles")
            .font(.caption.weight(.semibold))
            .foregroundStyle(MWPalette.navy.opacity(0.7))
            .accessibilityIdentifier("entertainmentLabel")
    }

    private var controls: some View {
        VStack(alignment: .leading, spacing: 18) {
            VStack(alignment: .leading, spacing: 9) {
                Text("WHAT WAS HAPPENING?")
                    .font(.caption.weight(.black))
                    .tracking(1.2)
                    .foregroundStyle(MWPalette.navy.opacity(0.65))
                Text("Optional context from you, not a guess from us.")
                    .font(.footnote)
                    .foregroundStyle(MWPalette.navy.opacity(0.72))

                ScrollView(.horizontal, showsIndicators: false) {
                    HStack(spacing: 8) {
                        ForEach(MomentContext.allCases) { context in
                            ContextChip(
                                context: context,
                                isSelected: draft.context == context,
                                action: {
                                    withAnimation(reduceMotion ? nil : .snappy) {
                                        draft.selectContext(draft.context == context ? nil : context)
                                    }
                                }
                            )
                        }
                    }
                }
            }

            Divider()

            VStack(alignment: .leading, spacing: 10) {
                Text("PLACE THE THOUGHT")
                    .font(.caption.weight(.black))
                    .tracking(1.2)
                    .foregroundStyle(MWPalette.navy.opacity(0.65))
                Text("Drag and pinch the bubble, or use these controls.")
                    .font(.footnote)
                    .foregroundStyle(MWPalette.navy.opacity(0.72))

                BubbleControls(layout: $draft.bubble)
            }

            Button {
                screen = .preview
            } label: {
                Label("Preview creation", systemImage: "play.fill")
                    .font(.headline)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 6)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .accessibilityIdentifier("previewButton")

            Text("The bubble stays fixed in the frame. It does not follow a moving pet.")
                .font(.caption)
                .foregroundStyle(MWPalette.navy.opacity(0.62))
                .frame(maxWidth: .infinity, alignment: .leading)
        }
        .padding(18)
        .background(.white.opacity(0.72), in: RoundedRectangle(cornerRadius: 24))
        .overlay {
            RoundedRectangle(cornerRadius: 24)
                .stroke(MWPalette.navy.opacity(0.09), lineWidth: 1)
        }
    }
}

private struct WelcomeView: View {
    let onTryDemo: () -> Void

    var body: some View {
        ScrollView {
            VStack(spacing: 24) {
                HStack {
                    VStack(alignment: .leading, spacing: 2) {
                        Text("MEWS")
                        Text("& WOOFS")
                    }
                    .font(.system(size: 16, weight: .black, design: .rounded))
                    .tracking(1.8)
                    .foregroundStyle(MWPalette.navy)
                    Spacer()
                    Label("Made locally", systemImage: "lock.fill")
                        .font(.caption.weight(.bold))
                        .foregroundStyle(MWPalette.navy.opacity(0.66))
                }

                WelcomeArtwork()
                    .frame(maxWidth: 540)
                    .aspectRatio(1.2, contentMode: .fit)

                VStack(spacing: 10) {
                    Text("What if that sound\nhad a punchline?")
                        .font(.largeTitle.weight(.black))
                        .fontDesign(.rounded)
                        .minimumScaleFactor(0.72)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(MWPalette.navy)
                    Text("Turn a short pet moment into a playful thought bubble you can make your own.")
                        .font(.body)
                        .multilineTextAlignment(.center)
                        .foregroundStyle(MWPalette.navy.opacity(0.72))
                        .frame(maxWidth: 460)
                }

                Button(action: onTryDemo) {
                    Label("Try a demo moment", systemImage: "waveform")
                        .font(.headline)
                        .frame(maxWidth: 360)
                        .padding(.vertical, 7)
                }
                .buttonStyle(.borderedProminent)
                .controlSize(.large)
                .accessibilityIdentifier("demoMomentButton")

                Text("The demo is built in; nothing is recorded. Responses are imagined for entertainment, never translation or advice.")
                    .font(.caption)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(MWPalette.navy.opacity(0.58))
                    .frame(maxWidth: 430)
                    .accessibilityIdentifier("premiseDisclosure")
            }
            .padding(.horizontal, 24)
            .padding(.vertical, 20)
            .frame(maxWidth: 760)
            .frame(maxWidth: .infinity)
        }
    }
}

private struct WelcomeArtwork: View {
    var body: some View {
        ZStack {
            RoundedRectangle(cornerRadius: 34)
                .fill(MWPalette.navy)
                .shadow(color: MWPalette.navy.opacity(0.18), radius: 24, y: 14)

            Circle()
                .fill(MWPalette.mint)
                .frame(width: 118)
                .offset(x: 115, y: -78)
                .blur(radius: 0.2)

            VStack(spacing: 12) {
                ThoughtShape()
                    .fill(.white)
                    .frame(width: 230, height: 102)
                    .overlay {
                        Text("Probably snacks.")
                            .font(.system(size: 20, weight: .black, design: .rounded))
                            .foregroundStyle(MWPalette.navy)
                            .padding(.horizontal, 24)
                    }
                    .rotationEffect(.degrees(-3))
                    .offset(x: 48)

                PetPortrait()
                    .frame(width: 180, height: 150)
                    .offset(x: -58)
            }

            WaveformMark()
                .stroke(MWPalette.coral, style: StrokeStyle(lineWidth: 7, lineCap: .round))
                .frame(width: 120, height: 54)
                .offset(x: 130, y: 105)
        }
        .padding(8)
        .accessibilityElement(children: .ignore)
        .accessibilityLabel("A playful pet portrait with a thought bubble saying, Probably snacks")
    }
}

struct MomentCanvas: View {
    @Binding var draft: CreationDraft
    let isPreview: Bool
    @State private var dragStart: BubbleLayout?
    @State private var scaleStart: CGFloat?

    var body: some View {
        GeometryReader { proxy in
            let size = proxy.size
            ZStack {
                LinearGradient(
                    colors: [MWPalette.navy, MWPalette.indigo],
                    startPoint: .topLeading,
                    endPoint: .bottomTrailing
                )

                Circle()
                    .fill(MWPalette.mint.opacity(0.92))
                    .frame(width: size.width * 0.45)
                    .position(x: size.width * 0.78, y: size.height * 0.19)

                RoundedRectangle(cornerRadius: size.width * 0.06)
                    .fill(MWPalette.coral.opacity(0.2))
                    .frame(width: size.width * 0.78, height: size.height * 0.26)
                    .rotationEffect(.degrees(-7))
                    .position(x: size.width * 0.38, y: size.height * 0.87)

                PetPortrait()
                    .frame(width: size.width * 0.62, height: size.height * 0.42)
                    .position(x: size.width * 0.48, y: size.height * 0.71)

                ThoughtBubble(text: draft.response.text)
                    .frame(width: min(size.width * 0.66, 290))
                    .scaleEffect(draft.bubble.scale)
                    .position(
                        x: size.width * draft.bubble.x,
                        y: size.height * draft.bubble.y
                    )
                    .gesture(dragGesture(in: size))
                    .simultaneousGesture(scaleGesture)
                    .allowsHitTesting(!isPreview)
                    .accessibilityLabel(draft.response.accessibilityText)
                    .accessibilityHint(
                        isPreview
                            ? "Fixed thought bubble in preview"
                            : "Drag or pinch, or use the editing controls below"
                    )
                    .accessibilityIdentifier("thoughtBubble")

                VStack {
                    Spacer()
                    HStack {
                        Label("PLAYFUL FICTION", systemImage: "sparkles")
                            .font(.system(size: 10, weight: .black, design: .rounded))
                            .tracking(1.1)
                            .foregroundStyle(.white.opacity(0.76))
                        Spacer()
                        Text("M&W")
                            .font(.system(size: 11, weight: .black, design: .rounded))
                            .foregroundStyle(.white.opacity(0.76))
                    }
                    .padding(14)
                }
            }
            .clipShape(RoundedRectangle(cornerRadius: 26))
            .overlay {
                RoundedRectangle(cornerRadius: 26)
                    .stroke(.white.opacity(0.36), lineWidth: 1)
            }
        }
        .aspectRatio(4 / 5, contentMode: .fit)
    }

    private func dragGesture(in size: CGSize) -> some Gesture {
        DragGesture()
            .onChanged { value in
                if dragStart == nil {
                    dragStart = draft.bubble
                }
                guard var updated = dragStart else { return }
                updated.move(
                    horizontal: value.translation.width / size.width,
                    vertical: value.translation.height / size.height
                )
                draft.bubble = updated
            }
            .onEnded { _ in dragStart = nil }
    }

    private var scaleGesture: some Gesture {
        MagnificationGesture()
            .onChanged { value in
                if scaleStart == nil {
                    scaleStart = draft.bubble.scale
                }
                guard let start = scaleStart else { return }
                draft.bubble.resize(to: start * value)
            }
            .onEnded { _ in scaleStart = nil }
    }
}

private struct ThoughtBubble: View {
    let text: String

    var body: some View {
        ThoughtShape()
            .fill(.white)
            .overlay {
                Text(text)
                    .font(.headline.weight(.black))
                    .fontDesign(.rounded)
                    .multilineTextAlignment(.center)
                    .foregroundStyle(MWPalette.navy)
                    .minimumScaleFactor(0.75)
                    .padding(.horizontal, 25)
                    .padding(.vertical, 23)
            }
            .frame(height: 126)
            .shadow(color: .black.opacity(0.17), radius: 12, y: 7)
    }
}

private struct ThoughtShape: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path(roundedRect: rect.insetBy(dx: 0, dy: rect.height * 0.09), cornerRadius: rect.height * 0.32)
        path.addEllipse(
            in: CGRect(
                x: rect.maxX * 0.72,
                y: rect.maxY * 0.78,
                width: rect.width * 0.12,
                height: rect.width * 0.12
            )
        )
        path.addEllipse(
            in: CGRect(
                x: rect.maxX * 0.84,
                y: rect.maxY * 0.91,
                width: rect.width * 0.055,
                height: rect.width * 0.055
            )
        )
        return path
    }
}

private struct PetPortrait: View {
    var body: some View {
        ZStack {
            Capsule()
                .fill(MWPalette.coral)
                .frame(width: 142, height: 108)
                .rotationEffect(.degrees(-8))
                .offset(y: 32)

            Path { path in
                path.move(to: CGPoint(x: 30, y: 58))
                path.addLine(to: CGPoint(x: 43, y: 8))
                path.addLine(to: CGPoint(x: 74, y: 34))
                path.addLine(to: CGPoint(x: 108, y: 7))
                path.addLine(to: CGPoint(x: 118, y: 60))
                path.closeSubpath()
            }
            .fill(MWPalette.warmWhite)
            .frame(width: 150, height: 92)
            .offset(y: -20)

            HStack(spacing: 34) {
                Circle().fill(MWPalette.navy).frame(width: 12, height: 12)
                Circle().fill(MWPalette.navy).frame(width: 12, height: 12)
            }
            .offset(y: -10)

            Capsule()
                .fill(MWPalette.navy)
                .frame(width: 22, height: 10)
                .offset(y: 14)
        }
    }
}

private struct WaveformMark: Shape {
    func path(in rect: CGRect) -> Path {
        var path = Path()
        let heights: [CGFloat] = [0.25, 0.72, 0.42, 1, 0.58, 0.82, 0.3]
        for (index, height) in heights.enumerated() {
            let x = rect.width * CGFloat(index) / CGFloat(heights.count - 1)
            path.move(to: CGPoint(x: x, y: rect.midY - rect.height * height * 0.5))
            path.addLine(to: CGPoint(x: x, y: rect.midY + rect.height * height * 0.5))
        }
        return path
    }
}

private struct ContextChip: View {
    let context: MomentContext
    let isSelected: Bool
    let action: () -> Void

    var body: some View {
        Button(action: action) {
            Label(context.title, systemImage: context.symbol)
                .font(.subheadline.weight(.bold))
                .padding(.horizontal, 13)
                .padding(.vertical, 9)
                .foregroundStyle(isSelected ? .white : MWPalette.navy)
                .background(
                    isSelected ? MWPalette.navy : MWPalette.cream,
                    in: Capsule()
                )
                .overlay {
                    Capsule().stroke(MWPalette.navy.opacity(isSelected ? 0 : 0.13), lineWidth: 1)
                }
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(isSelected ? .isSelected : [])
        .accessibilityIdentifier("context-\(context.rawValue)")
    }
}

private struct BubbleControls: View {
    @Binding var layout: BubbleLayout

    var body: some View {
        LazyVGrid(columns: Array(repeating: GridItem(.flexible(), spacing: 8), count: 4), spacing: 8) {
            control("Move left", symbol: "arrow.left") { layout.move(horizontal: -0.07, vertical: 0) }
            control("Move up", symbol: "arrow.up") { layout.move(horizontal: 0, vertical: -0.07) }
            control("Move down", symbol: "arrow.down") { layout.move(horizontal: 0, vertical: 0.07) }
            control("Move right", symbol: "arrow.right") { layout.move(horizontal: 0.07, vertical: 0) }
            control("Make smaller", symbol: "minus.magnifyingglass") { layout.resize(by: -0.1) }
            control("Make larger", symbol: "plus.magnifyingglass") { layout.resize(by: 0.1) }
            control("Reset bubble", symbol: "arrow.counterclockwise") { layout.reset() }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
    }

    private func control(_ label: String, symbol: String, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            Image(systemName: symbol)
                .frame(width: 28, height: 28)
        }
        .buttonStyle(.bordered)
        .accessibilityLabel(label)
        .accessibilityIdentifier(label.replacingOccurrences(of: " ", with: ""))
    }
}

private struct PreviewView: View {
    let draft: CreationDraft
    let onEdit: () -> Void
    let onFinish: () -> Void
    @State private var previewDraft: CreationDraft

    init(draft: CreationDraft, onEdit: @escaping () -> Void, onFinish: @escaping () -> Void) {
        self.draft = draft
        self.onEdit = onEdit
        self.onFinish = onFinish
        _previewDraft = State(initialValue: draft)
    }

    var body: some View {
        VStack(spacing: 16) {
            HStack {
                Button("Edit", systemImage: "chevron.left", action: onEdit)
                    .accessibilityIdentifier("editButton")
                Spacer()
                VStack(spacing: 1) {
                    Text("PREVIEW")
                        .font(.caption.weight(.black))
                        .tracking(1.4)
                    Text("Exactly as composed")
                        .font(.caption2)
                }
                .foregroundStyle(MWPalette.navy)
                Spacer()
                Button("Finish", action: onFinish)
                    .fontWeight(.bold)
                    .accessibilityIdentifier("finishButton")
            }

            MomentCanvas(draft: $previewDraft, isPreview: true)
                .frame(maxWidth: 540)
                .accessibilityIdentifier("previewCanvas")

            Label("Save and Share arrive with verified export", systemImage: "checkmark.seal")
                .font(.footnote.weight(.semibold))
                .foregroundStyle(MWPalette.navy.opacity(0.64))
        }
        .padding(.horizontal, 20)
        .padding(.vertical, 14)
        .frame(maxWidth: 720, maxHeight: .infinity, alignment: .top)
        .frame(maxWidth: .infinity, maxHeight: .infinity, alignment: .top)
    }
}

private enum MWPalette {
    static let cream = Color(red: 0.97, green: 0.94, blue: 0.87)
    static let warmWhite = Color(red: 1, green: 0.98, blue: 0.93)
    static let navy = Color(red: 0.08, green: 0.12, blue: 0.20)
    static let indigo = Color(red: 0.18, green: 0.19, blue: 0.39)
    static let coral = Color(red: 0.93, green: 0.34, blue: 0.28)
    static let mint = Color(red: 0.61, green: 0.88, blue: 0.75)
}

#Preview("Welcome") {
    ContentView()
}
