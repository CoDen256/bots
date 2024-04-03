package coden.dairy.reminder.notion

import notion.api.v1.NotionClient
import notion.api.v1.model.databases.*
import notion.api.v1.model.pages.PageProperty
import notion.api.v1.model.search.SearchResult
import notion.api.v1.request.search.SearchRequest

class NotionDairyTableUtility {
    companion object {

        fun NotionClient.create(path: NotionPath): NotionDairyTable {
            verifyUniqueness(path)
            val parent = path.parent() ?: throw IllegalArgumentException("$path must have at least one page parent to be created")
            val parentPageId = getPageId(parent)
            if (exists(path)) { return get(path) }
            val db = createDatabase(
                parent = DatabaseParent.page(parentPageId),
                title = path.title().asDatabaseRichText(),
                properties = SCHEMA
            )
            return NotionDairyTable(this, db.id)
        }

        fun NotionClient.exists(path: NotionPath): Boolean {
            return countDatabases(path) > 0
        }

        fun NotionClient.purge(path: NotionPath) {
            val repo = get(path)
            this.updatePage(repo.id, properties = mapOf(), archived = true)
        }

        fun NotionClient.get(path: NotionPath): NotionDairyTable {
            verifyUniqueness(path)
            val database = search(
                query = path.title(),
                filter = SearchRequest.SearchFilter("database", property = "object")
            )
                .results
                .firstOrNull { getDatabaseTitle(it) == path.title() }
            val id = database
                ?.id
                ?: throw IllegalStateException("$path table does not exist")
            return NotionDairyTable(this, id)
        }

        private fun NotionClient.getDatabase(path: NotionPath) = search(
            query = path.title(),
            filter = SearchRequest.SearchFilter("database", property = "object")
        )
            .results
            .firstOrNull { getDatabaseTitle(it) == path.title() }

        fun NotionClient.get(id: String): NotionDairyTable {
            return NotionDairyTable(this, id)
        }

        private fun NotionClient.verifyUniqueness(path: NotionPath) {
            val num = countDatabases(path)
            if (num > 1) {
                throw IllegalStateException("$path is duplicated $num times. But only one instance must be present")
            }
        }

        private fun NotionClient.getPageId(page: NotionPath): String {
            return search(
                query = page.title(),
                filter = SearchRequest.SearchFilter("page", property = "object")
            )
                .results
                .filter { getPageTitle(it) != null }
                .firstOrNull { getPageTitle(it) == page.title() }
                ?.id
                ?: throw IllegalStateException("Create page $page and add connection")
        }

        private fun NotionClient.countDatabases(db: NotionPath): Int {
            return search(
                query = db.title(),
                filter = SearchRequest.SearchFilter("database", property = "object")
            )
                .results
                .count { getDatabaseTitle(it) == db.title() }
        }

        private fun getPageTitle(it: SearchResult) = it.asPage().properties["title"]?.title?.get(0)?.plainText
        private fun getDatabaseTitle(it: SearchResult) = it.asDatabase().title?.get(0)?.plainText

        fun String.asRichText(): List<PageProperty.RichText> =
            listOf(PageProperty.RichText(text = PageProperty.RichText.Text(content = this)))

        fun String.asDatabaseRichText(): List<DatabaseProperty.RichText> =
            listOf(DatabaseProperty.RichText(text = DatabaseProperty.RichText.Text(content = this)))
    }
}
