package ${@pkg}
{
	import ${@global.@defaultPKG}.types.*;
	import ${@global.@defaultPKG}.types.response.*;
	
	import com.vox.future.request.BaseMessageType;
	import flash.utils.Dictionary;
	
	/**
	 * ${@comment}
	 */
	public class ${@name} extends BaseMessageType
	{
		$[for ${var} in ${@variables}]
		protected var _${var.@name}:$[if ${var.@isMap}]Dictionary$[else if ${var.@isArray}]Vector.<${var.@type}>$[else]${var.@type}$[end if];
		/** ${var.@comment} */
		public function get ${var.@name}():$[if ${var.@isMap}]Dictionary$[else if ${var.@isArray}]Vector.<${var.@type}>$[else]${var.@type}$[end if]
		{
			return _${var.@name};
		}
		$[end for]
		
		public function ${@name}()
		{
			super();
			$[for ${var} in ${@variables}]$[if ${var.@isCustomType}]$[if ${var.@isArray}]$[else]//_${var.@name} = new ${var.@type}();
			$[end if]$[end if]$[end for]
		}
		
		override public function pack():Object
		{
			var data:Object = {};
			$[for ${var} in ${@variables}]data.${var.@name} = type2Object(${var.@name});
			$[end for]return data;
		}
		
		override public function parse(data:Object):BaseMessageType
		{
			if(data == null) return null;
			super.parse(data);

			$[for ${var} in ${@variables}]_${var.@name} = obj2Type(data.${var.@name}, $[if ${var.@isMap}]$[if ${var.@isArray}](Vector.<${var.@type}>) as Class, ${var.@keyType}$[else]${var.@type}, ${var.@keyType}$[end if]$[else]$[if ${var.@isArray}](Vector.<${var.@type}>) as Class$[else]${var.@type}$[end if]$[end if]);
			$[end for]
			return this;
		}
	}
}