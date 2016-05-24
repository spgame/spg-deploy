package ${@pkg}
{
	import ${@global.@defaultPKG}.types.*;
	import ${@global.@defaultPKG}.types.response.*;
	
	import com.vox.future.request.BaseMessageType;
	import com.vox.games.specialGame.evolve.SPGBaseMessageType;
	import flash.utils.Dictionary;
	
	/**
	 * ${@comment}
	 */
	public class ${@name} extends SPGBaseMessageType
	{
		public function ${@name}(rawData:* = undefined)
		{
			super(rawData);
		}
		
		$[for ${var} in ${@variables}]
		private var _${var.@name}_isInited:Boolean;
		private var _${var.@name}:$[if ${var.@isMap}]Dictionary$[else if ${var.@isArray}]Vector.<${var.@type}>$[else]${var.@type}$[end if];
		/** ${var.@comment} */
		public function get ${var.@name}():$[if ${var.@isMap}]Dictionary$[else if ${var.@isArray}]Vector.<${var.@type}>$[else]${var.@type}$[end if]
		{
			if(!_${var.@name}_isInited)
			{
				if(null != rawData.${var.@name})
				{$[if ${var.@isMap}]$[if ${var.@isArray}]/**是值为Vector的Dictionary*/
					_${var.@name} = new Dictionary();
					fillingDyadicArray(rawData.${var.@name}, _${var.@name}, Vector.<${var.@type}>, ${var.@type});
				$[else]/**是Dictionary*/
					_${var.@name} = new Dictionary();
					fillingArray(rawData.${var.@name}, _${var.@name}, ${var.@type});
				$[end if]$[else]$[if ${var.@isArray}]/**是Vector*/
					_${var.@name} = new Vector.<${var.@type}>();
					fillingArray(rawData.${var.@name}, _${var.@name}, ${var.@type});
				$[else]$[if ${var.@isCustomType}]/**是SPGBaseMessageType*/
					_${var.@name} = new ${var.@type}();
					_${var.@name}.parse(rawData.${var.@name});
				$[else]/**是原生类型*/
					_${var.@name} = (${var.@type})(rawData.${var.@name});$[end if]$[end if]$[end if]
				}
				_${var.@name}_isInited = true;
			}
			
			return _${var.@name};
		}
		$[end for]
	}
}