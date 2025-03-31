package io.github.coden256.journal.notion

import io.github.coden256.journal.core.persistance.JournalEntry
import io.github.coden256.journal.core.persistance.JournalRepository
import io.github.coden256.journal.notion.NotionDairyTableUtility.Companion.asRichText
import notion.api.v1.NotionClient
import notion.api.v1.model.databases.DatabaseProperty
import notion.api.v1.model.databases.DatabasePropertySchema
import notion.api.v1.model.databases.RichTextPropertySchema
import notion.api.v1.model.databases.TitlePropertySchema
import notion.api.v1.model.databases.query.filter.QueryTopLevelFilter
import notion.api.v1.model.pages.Page
import notion.api.v1.model.pages.PageParent
import notion.api.v1.model.pages.PageProperty
import java.time.YearMonth
import java.time.format.DateTimeFormatter

val SCHEMA: Map<String, DatabasePropertySchema> = mapOf(
    "Month" to TitlePropertySchema(),
    "Description" to RichTextPropertySchema()
)

class NotionJournalTable(
    private val client: NotionClient,
    val id: String
) : JournalRepository {

    private val formatter: DateTimeFormatter = DateTimeFormatter.ofPattern("MM'/'yyyy")


    private val db = client.retrieveDatabase(id)

    init {
        verifySchema(db.properties, SCHEMA)
    }


    private fun verifySchema(
        properties: Map<String, DatabaseProperty>,
        target: Map<String, DatabasePropertySchema>
    ): Boolean {
        if (target.size != properties.size) throw IllegalStateException("${db.title} does not match schema of DairyRepository: expected <${target.size}> elements, but was <${properties.size}>")
        for ((k, v) in target) {
            val property = properties.getOrElse(k) {
                throw IllegalStateException("${db.title} does not match schema of DairyRepository: '$k' property is missing in the table")
            }
            val type = v.javaClass.simpleName.removeSuffix("PropertySchema")
            val actual = property.type.name
            if (actual != type) {
                throw IllegalStateException("${db.title} does not match schema of DairyRepository: '$k' must have <$type> type but was: <$actual>")

            }
        }
        return true
    }

    override fun entries(): Result<Collection<JournalEntry>> {
        return Result.success(Unit)
            .mapCatching {
                queryPages().mapNotNull { mapFromPage(it) }
            }
    }

    private fun queryPages(filter: QueryTopLevelFilter? = null) =
        client.queryDatabase(id, filter).results

    override fun get(month: YearMonth): Result<JournalEntry> {
        return entries()
            .getOrNull()
            ?.firstOrNull { it.month == month }
            ?.let { Result.success(it) }
            ?: Result.failure(IllegalArgumentException("No entry for $month"))
    }


    override fun first(): Result<JournalEntry> {
        return entries()
            .getOrNull()
            ?.minByOrNull { it.month }?.let { Result.success(it) }
            ?: Result.failure(IllegalArgumentException("No entries"))
    }

    override fun last(): Result<JournalEntry> {
        return entries()
            .getOrNull()
            ?.maxByOrNull { it.month }?.let {
                Result.success(it)
            } ?: Result.failure(IllegalArgumentException("No entries"))
    }

    override fun insert(entry: JournalEntry): Result<Unit> {
        return Result
            .success(Unit)
            .mapCatching {
                client.createPage(
                    parent = PageParent.database(id),
                    properties = mapToProperties(entry)
                )
            }
    }

    private fun mapFromPage(page: Page): JournalEntry? {
        val descirption = getProperty(page, "Description").richText?.firstOrNull()?.plainText
        val month = getProperty(page, "Month").title?.firstOrNull()?.plainText
        if (descirption == null || month.isNullOrBlank()) return null
        return JournalEntry(
            YearMonth.parse(month, formatter),
            descirption
        )
    }

    private fun getProperty(
        page: Page,
        prop: String
    ) = page.properties[prop] ?: throw IllegalArgumentException("Unknown page format: $page, missing 'Description'")

    private fun mapToProperties(entry: JournalEntry): Map<String, PageProperty> {
        return mapOf(
            "Month" to PageProperty(title = formatter.format(entry.month).asRichText()),
            "Description" to PageProperty(richText = entry.description.asRichText())
        )
    }

    override fun delete(month: YearMonth): Result<Unit> {
        return Result.success(Unit)
            .mapCatching {
                queryPages()
                    .mapNotNull { page -> mapFromPage(page)?.let { it to page } }
                    .firstOrNull { it.first.month == month }
                    ?.let {
                        deletePage(it.second)
                    }
            }
    }

    override fun clear(): Result<Long> {
        var counter = 0L
        queryPages()
            .forEach {
                deletePage(it)
                counter++
            }
        return Result.success(counter)
    }

    private fun deletePage(it: Page) {
        client.updatePage(
            pageId = it.id,
            properties = it.properties,
            archived = true
        )
    }
}