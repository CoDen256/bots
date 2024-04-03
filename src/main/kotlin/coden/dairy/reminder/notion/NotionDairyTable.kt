package coden.dairy.reminder.notion

import coden.dairy.reminder.model.DairyEntry
import coden.dairy.reminder.model.DairyRepository
import notion.api.v1.NotionClient
import notion.api.v1.model.databases.DatabaseProperty
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


    private val db = client.retrieveDatabase(id)
    init {
        verifySchema(db.properties, SCHEMA)
    }


    private fun verifySchema(properties: Map<String, DatabaseProperty>, target: Map<String, DatabasePropertySchema>): Boolean{
        if (target.size != properties.size) throw IllegalStateException("${db.title} does not match schema of DairyRepository: expected <${target.size}> elements, but was <${properties.size}>")
        for ((k,v) in target){
            val property = properties.getOrElse(k){
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

    override fun entries(): Collection<DairyEntry> {
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