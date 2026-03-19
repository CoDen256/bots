import logging
import telebot
import functools

log = logging.getLogger("TelegramBot")

class TelegramBot:
    def __init__(self, token):
        self.delegate = telebot.TeleBot(token)

    def start_blocking(self):
        log.info("Starting telegram bot!")
        self.delegate.infinity_polling()

    def pin(self, message, **kwargs):
        try:
            return self.delegate.pin_chat_message(message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, "Could not pin")

    def unpin(self, message, **kwargs):
        try:
            return self.delegate.unpin_chat_message(message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, "Could not unpin")

    def get_chat(self, message):
        try:
            return self.delegate.get_chat(message.chat.id)
        except Exception as e:
            self.error(message, e, "Could not get chat: " + message.chat.id)

    def create_topic(self, message, topic, **kwargs):
        try:
            return self.delegate.create_forum_topic(message.chat.id, topic, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not create forum: {topic}")

    def delete(self, message, **kwargs):
        try:
            return self.delegate.delete_message(message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, "Could not delete")

    def copy(self, message, **kwargs):
        try:
            id = self.delegate.copy_message(message.chat.id, message.chat.id, message.message_id, **kwargs).message_id
            new = Message.de_json(message.json)
            new.id = id
            new.message_id = id
            return new
        except Exception as e:
            self.error(message, e, f"Could not copy message")

    def send(self, message, text, **kwargs):
        try:
            return self.delegate.send_message(message.chat.id, text, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not send: {text}")

    def edit(self, message, text, **kwargs):
        try:
            if message.content_type != "text":
                if message.caption == text: return None
                return self.delegate.edit_message_caption(text, message.chat.id, message.message_id, **kwargs)

            if message.text == text or not text: return None
            return self.delegate.edit_message_text(text, message.chat.id, message.message_id, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not edit to: {text}")

    def reply(self, message, text, **kwargs):
        try:
            return self.delegate.reply_to(message, text, **kwargs)
        except Exception as e:
            self.error(message, e, f"Could not reply: {text}")

    def error(self, message, error, additional_info=None):
        result = f"❌ {additional_info if additional_info else ''}\n{error}"
        print(result.replace("\n", " ") + " Message: " + str(message.text))
        self.delegate.reply_to(message, result)

    def error(self, message, error, additional_info=None):
        result = f"❌ {additional_info if additional_info else ''}\n{error}"
        print(result.replace("\n", " ") + " Message: " + str(message.text))
        self.delegate.reply_to(message, result)

    def __getattr__(self, name):
        attr = getattr(self.delegate, name)
        if callable(attr):
            return self._wrap_registrar(attr)
        return attr

    def _wrap_registrar(self, registrar):
        """Intercepts decorator calls like message_handler(...) and wraps the handler."""
        def registrar_proxy(*args, **kwargs):
            decorator = registrar(*args, **kwargs)
            def decorator_proxy(fn):
                @functools.wraps(fn)
                def safe_handler(message, *fn_args, **fn_kwargs):
                    try:
                        return fn(message, *fn_args, **fn_kwargs)
                    except Exception as e:
                        self.error(message, e, f"{fn.__name__} failed")
                return decorator(safe_handler)
            return decorator_proxy
        return registrar_proxy