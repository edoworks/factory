import SwiftUI

struct ContentView: View {
    @State private var items: [String] = []
    @State private var newItemText = ""

    var body: some View {
        NavigationStack {
            Group {
                if items.isEmpty {
                    EmptyStateView()
                } else {
                    List {
                        ForEach(items, id: \.self) { item in
                            Text(item)
                        }
                        .onDelete(perform: deleteItems)
                    }
                }
            }
            .navigationTitle("AppTemplate")
            .toolbar {
                ToolbarItem(placement: .primaryAction) {
                    Button(action: addItem) {
                        Label("Add Item", systemImage: "plus")
                    }
                }
                if !items.isEmpty {
                    ToolbarItem(placement: .topBarLeading) {
                        ShareLink(item: items.joined(separator: "\n")) {
                            Label("Export", systemImage: "square.and.arrow.up")
                        }
                    }
                }
            }
            .overlay {
                if !newItemText.isEmpty {
                    AddItemSheet(
                        text: $newItemText,
                        onAdd: confirmAdd,
                        onCancel: cancelAdd
                    )
                }
            }
        }
    }

    private func addItem() {
        newItemText = " "
    }

    private func confirmAdd() {
        let trimmed = newItemText.trimmingCharacters(in: .whitespacesAndNewlines)
        if !trimmed.isEmpty {
            items.append(trimmed)
        }
        newItemText = ""
    }

    private func cancelAdd() {
        newItemText = ""
    }

    private func deleteItems(at offsets: IndexSet) {
        items.remove(atOffsets: offsets)
    }
}

struct EmptyStateView: View {
    var body: some View {
        ContentUnavailableView(
            "No Items Yet",
            systemImage: "tray",
            description: Text("Tap + to add your first item.")
        )
        .accessibilityLabel("No items yet")
        .accessibilityHint("Tap the plus button to add your first item")
    }
}

struct AddItemSheet: View {
    @Binding var text: String
    let onAdd: () -> Void
    let onCancel: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Text("New Item")
                .font(.headline)
            TextField("Enter item text", text: $text)
                .textFieldStyle(.roundedBorder)
                .autocorrectionDisabled()
            HStack(spacing: 12) {
                Button("Cancel", role: .cancel, action: onCancel)
                Button("Add", action: onAdd)
                    .buttonStyle(.borderedProminent)
            }
        }
        .padding(24)
        .frame(maxWidth: 320)
        .background(.regularMaterial)
        .cornerRadius(16)
        .shadow(radius: 8)
        .accessibilityElement(children: .contain)
    }
}

#Preview {
    ContentView()
}