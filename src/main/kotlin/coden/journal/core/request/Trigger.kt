package coden.journal.core.request

import java.io.Closeable

interface Trigger: Closeable {
    fun start()
}