package io.github.coden.focus.observer.telegram

import io.github.coden.telegram.keyboard.Keyboard
import io.github.coden.telegram.keyboard.KeyboardButton
import io.github.coden.telegram.keyboard.keyboard
import io.github.coden.utils.success


// 12x8 + 4x1 = 100 max
fun <T> keyboard(elements: List<T>, columns: Int, createButton: (T) -> KeyboardButton): Result<Keyboard>{
    if (elements.size > 100){ return Result.failure(IllegalArgumentException("Could have only create less than 100 buttons, but was: ${elements.size}")) }

    return keyboard {
        elements
            .chunked(columns)
            .forEach { chunk ->
                this.row{
                    chunk.forEach { action ->
                        b(createButton(action))
                    }
                }
            }
    }.success()
}