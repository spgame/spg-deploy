package ${@defaultPKG}
{
	import flash.utils.Dictionary;
	$[for ${msg} in ${@messages}]import ${msg.@pkg}.${msg.@name}Command;
	$[end for]
	public class StaticMessageType
	{
		private static var _commandDict:Dictionary = new Dictionary();
		/** 获取命令字典 */
		public static function get commandDict():Dictionary
		{
			return _commandDict;
		}
		$[for ${msg} in ${@messages}]_commandDict["${msg.@name}"] = ${msg.@name}Command;
		$[end for]
		$[for ${msg} in ${@messages}]/**
		 * ${msg.@comment}
		 */
		public static const ${msg.@name}:String = "${msg.@name}";
		$[end for]
	}
}