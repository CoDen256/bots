package io.github.coden.focus.observer.telegram

import io.github.coden.telegram.db.BotDB
import io.github.coden.telegram.db.db
import org.telegram.abilitybots.api.db.MapDBContext

class FocusObserverDB(filename: String)
    :MapDBContext(db( filename)), BotDB  {
}