package ${@pkg}
{
	import com.vox.future.notifications.events.GetServerResponseEvent;
	import com.vox.future.request.BaseMessageType;
	import com.vox.future.request.BaseRequestCommand;
	import com.vox.future.request.BaseRequestMessage;
	import ${@global.@defaultPKG}.types.*;
	import ${@global.@defaultPKG}.types.response.*;
	import ${@responseType.@pkg}.${@responseType.@name};
	import com.vox.games.specialGame.util.loader.LoadAsset;
	
	import flash.events.ErrorEvent;
	import flash.events.IEventDispatcher;
	
	/**
	 * ${@comment}
	 */
	public class ${@name}Command extends BaseRequestCommand
	{
		[Inject]
		public var dispatcher:IEventDispatcher;
		
		public function ${@name}Command()
		{
			super();
		}
		
		override public function execute():void
		{
			var msg:${@name}Message = BaseRequestMessage.requestMSG as ${@name}Message;
			this.msg = msg;
			
			LoadAsset.loadStaticJson(msg.url, complete, error);
				
			function complete(result:String):void
			{
				var jsonObj:Object = JSON.parse('{"list":' + result + '}');
				onComplete(jsonObj, msg.url, null);
			}
			function error(event:ErrorEvent):void
			{
				onError(event, msg.url, null);
			}
		}
		
		override protected function packMessage():Object
		{
			var msg:${@name}Message = this.msg as ${@name}Message;
			var data:Object = {};
			data.securityKey = msg.securityKey;
			$[for ${var} in ${@variables}]$[if ${var.@isArray}]data.${var.@name} = packArray(msg.${var.@name});
			$[else if ${var.@isCustomType}]data.${var.@name} = msg.${var.@name}.pack();
			$[else]data.${var.@name} = msg.${var.@name};
			$[end if]$[end for]return data;
		}
		
		override public function onResponse(result:Object):void
		{
			var response:${@responseType.@name} = new ${@responseType.@name}();
			response.parse(result);
			var event:GetServerResponseEvent = new GetServerResponseEvent(response, this.msg);
			dispatcher.dispatchEvent(event);
		}
	}
}