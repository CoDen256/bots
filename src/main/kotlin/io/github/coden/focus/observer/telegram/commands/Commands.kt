package io.github.coden.focus.observer.telegram.commands

import io.github.coden.telegram.abilities.replyOnCallback
import io.github.coden.utils.success
import org.apache.logging.log4j.kotlin.logger
import org.telegram.abilitybots.api.objects.Reply
import org.telegram.telegrambots.meta.api.objects.Update
import kotlin.reflect.KClass
import kotlin.reflect.KType
import kotlin.reflect.KVisibility
import kotlin.reflect.full.memberProperties
import kotlin.reflect.full.primaryConstructor

sealed interface CallbackCommand

interface CommandSerializer<C : CallbackCommand> {
    fun deserialize(data: String): Result<C>
    fun serialize(command: C): String
}

class DefaultCommandSerializer<C : CallbackCommand>(
    private val argsSeparator: String,
    target: KClass<out C>
) : CommandSerializer<C> {

    private val commands: Map<String, ClassWithArity> by lazy {
        target
            .sealedSubclasses
            .filter { it.isFinal } // data class or objects
            .filter { it.simpleName != null }
            .associate { it.simpleName!! to ClassWithArity(it, getArity(it)) }
    }

    private fun getArity(`class`: KClass<out C>): List<KType> {
        return `class`
            .primaryConstructor
            ?.parameters
            ?.map { it.type }
            ?: emptyList()
    }

    private inner class ClassWithArity(
        val target: KClass<out C>,
        val parameters: List<KType>
    ) {
        val arity: Int
            get() = parameters.size

        override fun toString(): String {
            return "${target.simpleName}($arity)"
        }
    }

    override fun deserialize(data: String): Result<C> {
        val args = ArrayList(data.split(argsSeparator))
        val cmdName = args.removeFirst()
        if (cmdName.isBlank()) return Result.failure(IllegalArgumentException("Command was not provided: <$data>"))

        val cmdClass: ClassWithArity = commands[cmdName]
            ?: return Result.failure(ClassNotFoundException("Command with name <$cmdName> not found. Possible values are ${commands.values}"))
        if (args.size != cmdClass.arity) return Result.failure(IllegalArgumentException("Provided <$cmdClass> has invalid arity, was: ${args.size}"))

        return cmdClass.target.objectInstance?.success()
            ?: instantiateViaConstructor(cmdClass, args)
    }

    private fun instantiateViaConstructor(
        cmdClass: ClassWithArity,
        args: List<String>
    ): Result<C> {
        val target = cmdClass.target
        val primaryConstructor = target.primaryConstructor
            ?: return Result.failure(IllegalArgumentException("<$cmdClass> has no primary constructor."))
        return try {
             primaryConstructor.call(
                *cmdClass
                    .parameters
                    .zip(args)
                    .map { (type, arg) -> deserializeParameters(type, arg) }
                    .toTypedArray()
            ).success()
        } catch (e: Exception) {
            Result.failure(e)
        }

    }

    private fun deserializeParameters(it: KType, arg: String): Any {
        val classifier: KClass<*>? = it.classifier as? KClass<*>
        return when(classifier) {
            null -> throw IllegalArgumentException("Classifier of $it for $arg is not provided")
            String::class -> arg
            Int::class -> arg.toInt()
            Long::class -> arg.toLong()
            else -> {
                throw ClassNotFoundException("Cannot deserialize <$it> from <$arg>: $it is a unknown type")
            }
        }
    }

//  if (classifier.isSubclassOf(Enum::class)){return read(classifier, arg) }
    fun <T : Enum<T>> read(type: KClass<T>, arg: String): T {
        return java.lang.Enum.valueOf(type.java, arg)
    }

    override fun serialize(command: C): String {
        val result = mutableListOf(command::class.simpleName)

        result.addAll(command::class
            .memberProperties
            .filter { it.visibility == KVisibility.PUBLIC }
            .map { it.getter.call(command) }
            .map { it.toString() }
        )
        return result.joinToString(argsSeparator)
    }
}

inline fun <reified C: CallbackCommand> commandSerializer(separator: String = "$"): CommandSerializer<C>{
    return DefaultCommandSerializer(separator, C::class)
}

fun <C: CallbackCommand> CommandSerializer<C>.replyOnCallbackCommand(handle: (Update, C) -> Unit): Reply {
    return replyOnCallback { upd, data ->
        logger("Processing callback command: $data")
        handle(upd, deserialize(data).getOrThrow())
    }
}