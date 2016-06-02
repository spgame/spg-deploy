package ${@pkg}
{
	import com.vox.future.managers.ContextManager;
	import com.vox.future.services.GameCommonService;
	import com.vox.games.specialGame.evolve.SPGBaseRequestMessage;
	import ${@global.@defaultPKG}.types.*;
	import ${@global.@defaultPKG}.types.extra.*;//为extra打桩
	import ${@global.@defaultPKG}.types.response.*;
	import ${@global.@defaultPKG}.MessageType;
	
	/**
	 * ${@comment}
	 */
	public class ${@name}Message extends SPGBaseRequestMessage
	{
		$[for ${var} in ${@variables}]
		$[if ${var.@isArray}]/**
		 * ${var.@comment}
		 * ${var.@type} 类型的数组
		 */
		public var ${var.@name}:Array;${var.@type};// 打桩
		$[else]/** ${var.@comment} */
		public var ${var.@name}:${var.@type};
		$[end if]$[end for]
		override public function get url():String
		{
			var service:GameCommonService = ContextManager.context.getObjectByType(GameCommonService);
			return service.requestUrlBase + "${@url}";
		}
		
		public function ${@name}Message()
		{
			super(MessageType.${@name});
			$[for ${var} in ${@variables}]$[if ${var.@isCustomType}]$[if ${var.@isArray}]$[else]this.${var.@name} = new ${var.@type}();
			$[end if]$[end if]$[end for]
		}
	}
}