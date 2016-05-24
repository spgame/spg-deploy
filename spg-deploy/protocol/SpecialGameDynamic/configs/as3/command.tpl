package ${@pkg}
{
	import ${@global.@defaultPKG}.types.*;
	import ${@global.@defaultPKG}.types.response.*;
	import ${@responseType.@pkg}.${@responseType.@name};
	import com.vox.games.specialGame.evolve.SPGBaseRequestCommand;
	import com.vox.games.specialGame.evolve.SPGBaseRequestMessage;
	import com.vox.games.specialGame.evolve.SPGGetServerResponseEvent;
	
	/**
	 * ${@comment}
	 */
	public class ${@name}Command extends SPGBaseRequestCommand
	{
		[Inject]
		public var _msg:${@name}Message;
		public override function get msg():SPGBaseRequestMessage
		{
			return _msg;
		}
		$[if ${@sign}]//override protected function get needSign():Boolean
		//{
		//	return true;
		//}$[end if]
		override protected function get name():String
		{
			return "${@name}";
		}
		
		override protected function packMessage():Object
		{
			var ret:Object = {};
			$[for ${var} in ${@variables}]$[if ${var.@isArray}]ret.${var.@name} = packArray(_msg.${var.@name});
			$[else if ${var.@isCustomType}]ret.${var.@name} = _msg.${var.@name}.pack();
			$[else]ret.${var.@name} = _msg.${var.@name};
			$[end if]$[end for]return ret;
		}
		
		override public function onResponse(result:Object):void
		{
			var response:${@responseType.@name} = new ${@responseType.@name}();
			response.parse(result);
			var event:SPGGetServerResponseEvent = new SPGGetServerResponseEvent(response, this.msg);
			eventDispatcher.dispatchEvent(event);
		}
	}
}