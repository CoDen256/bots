package io.github.coden256.focus.telegram

import io.github.coden256.telegram.keyboard.Keyboard
import io.github.coden256.telegram.keyboard.KeyboardButton
import io.github.coden256.telegram.keyboard.keyboard
import io.github.coden256.utils.success


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