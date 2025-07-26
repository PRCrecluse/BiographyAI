1.supabase.swift:
import Foundation
import Supabase

let supabase = SupabaseClient(
  supabaseURL: URL(string: "https://your-project-id.supabase.co")!,
  supabaseKey: "your-supabase-anon-key-here"
)
        
2.todo.swift
import Foundation

struct Todo: Identifiable, Decodable {
  var id: Int
  var title: String
}

3.contentview.swift:

import Supabase
import SwiftUI

struct ContentView: View {
  @State var todos: [Todo] = []

  var body: some View {
    NavigationStack {
      List(todos) { todo in
        Text(todo.title)
      }
      .navigationTitle("Todos")
      .task {
        do {
          todos = try await supabase.from("todos").select().execute().value
        } catch {
          debugPrint(error)
        }
      }
    }
  }
}

#Preview {
  ContentView()
}

