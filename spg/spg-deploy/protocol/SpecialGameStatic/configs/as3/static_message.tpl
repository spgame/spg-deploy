package ${@pkg}
{
	import com.vox.future.managers.ContextManager;
	import com.vox.future.request.BaseRequestMessage;
	import com.vox.future.services.GameCommonService;
	import ${@global.@defaultPKG}.types.*;
	import ${@global.@defaultPKG}.types.response.*;
	import ${@global.@defaultPKG}.StaticMessageType;
	
	import flash.utils.getQualifiedClassName;
	
	/**
	 * ${@comment}
	 */
	public class ${@name}Message extends BaseRequestMessage
	{
		internal var _data:Object;
		
		/** 当前UserId+securityKey，再MD5加密，将加密后的字符串在方法调用时返回 */
		public var securityKey:String;
		
		public function ${@name}Message()
		{
			super(StaticMessageType.${@name});
			$[for ${var} in ${@variables}]$[if ${var.@isCustomType}]$[if ${var.@isArray}]$[else]this.${var.@name} = new ${var.@type}();
			$[end if]$[end if]$[end for]
		}

		
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
			return "${@url}"
		}
		
		override public function get data():Object
		{
			return _data;
		}
	}
}