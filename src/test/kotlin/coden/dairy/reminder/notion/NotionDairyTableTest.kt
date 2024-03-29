package coden.dairy.reminder.notion

import notion.api.v1.NotionClient
import notion.api.v1.request.search.SearchRequest
import org.junit.jupiter.api.Order

import org.junit.jupiter.api.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class NotionDairyTableTest {

    private val token = "secret_onegyirr9ANiY7fs3lp5uUjNjXuehh8AxrIzbVdPNGJ"
    private val notion = NotionClient(token)
    private val path = NotionPath("/Junit Test")
    private val repository: NotionDairyTable = NotionDairyTable(notion, path)


    @Test
    @Order(0)
    fun create() {
        repository.create()

        println(notion)
    }

    @Test
    fun entries() {
        val findPage = repository.findPage()
        println(findPage)
    }

    @Test
    fun get() {
    }

    @Test
    fun first() {
    }

    @Test
    fun last() {
    }

    @Test
    fun insert() {
    }

    @Test
    fun delete() {
    }



    @Test
    fun purge() {
    }

    @Test
    fun clear() {
    }

    @Test
    fun close() {
    }
}