package coden.dairy.reminder.notion

import coden.dairy.reminder.core.DairyEntry
import coden.dairy.reminder.core.DairyRepository
import notion.api.v1.NotionClient
import notion.api.v1.model.databases.*
import notion.api.v1.model.pages.PageParent
import notion.api.v1.model.pages.PageProperty
import notion.api.v1.model.search.SearchResult
import notion.api.v1.request.search.SearchRequest
import java.io.Closeable
import java.util.stream.Stream





fun main() {
    NotionClient(token = "secret_onegyirr9ANiY7fs3lp5uUjNjXuehh8AxrIzbVdPNGJ").use { client ->
        // Find the "Test Database" from the list
//        val database = client
//            .search(
//                query = "Test Database",
//                filter = SearchRequest.SearchFilter("database", property = "object")
//            )
//            .results
//            .find { it.asDatabase().properties.containsKey("Severity") }
//            ?.asDatabase()
//            ?: error("Create a database named 'Test Database' and invite this app's user!")
        // Alternatively if you know the UUID of the Database, use `val database = client.retrieveDatabase("...")`.

        val database = client.retrieveDatabase("c14f4828-2090-4e5b-aa64-e290a18a181d")

//        database.properties[""]
        // All the options for "Severity" property (select type)
//        val severityOptions = database.properties["Severity"]!!.select!!.options!!
//         All the options for "Tags" property (multi_select type)
//        val tagOptions = database.properties["Tags"]!!.multiSelect!!.options!!
//         A user object for "Assignee" property (people type)
//        val assignee = client.listUsers().results.first() // Just picking a random user.

        // Create a new page in the database
//        val newPage = client.createPage(
//            // Use the "Test Database" as this page's parent
//            parent = PageParent.database(database.id),
//            // Set values to the page's properties
//            // (Values of referenced options, people, and relations must be pre-defined before this API call!)
//            properties = mapOf(
//                "Month" to PageProperty(title = "2022/01".asRichText()),
//                "Description" to PageProperty(richText = "hello".asRichText()),
//                "URL" to PageProperty(url = "https://www.example.com"),
//            )
//        )

//        // Properties can be addressed by their ID too.
//        val severityId = newPage.properties["Severity"]!!.id
//
//        // Update properties in the page
//        val updatedPage = client.updatePage(
//            pageId = newPage.id,
//            // Update only "Severity" property
//            properties = mapOf(
//                severityId to PageProperty(select = severityOptions.single { it.name == "Medium" }),
//            )
//        )
//
//        // Fetch the latest data of the page
//        val retrievedPage = client.retrievePage(newPage.id)
//
//        println(retrievedPage)
    }
}

