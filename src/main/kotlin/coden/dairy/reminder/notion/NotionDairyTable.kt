package coden.dairy.reminder.notion

import coden.dairy.reminder.model.DairyEntry
import coden.dairy.reminder.model.DairyRepository
import notion.api.v1.NotionClient
import notion.api.v1.model.databases.DatabasePropertySchema
import notion.api.v1.model.databases.RichTextPropertySchema
import notion.api.v1.model.databases.TitlePropertySchema
import java.util.stream.Stream

val SCHEMA: Map<String, DatabasePropertySchema> = mapOf(
    "Month" to TitlePropertySchema(),
    "Description" to RichTextPropertySchema()
)

class NotionDairyTable(
    private val client: NotionClient,
    val id: String
) : DairyRepository {



    override fun entries(): Stream<DairyEntry> {
        TODO("Not yet implemented")
    }

    override fun get(index: Int): DairyEntry {
        TODO("Not yet implemented")
    }

    override fun first(): DairyEntry {
        TODO("Not yet implemented")
    }

    override fun last(): DairyEntry {
        TODO("Not yet implemented")
    }

    override fun insert(entry: DairyEntry) {
        TODO("Not yet implemented")
    }

    override fun delete(index: Int) {
        TODO("Not yet implemented")
    }

    override fun clear() {
        TODO("Not yet implemented")
    }
}