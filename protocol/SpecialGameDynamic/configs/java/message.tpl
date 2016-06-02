package ${@pkg};

import com.voxlearning.utopia.entity.flashmsg.AbstractMessageBean;
import com.a17zuoye.commons.lang.json.JsonUtils;
import java.io.Serializable;
import java.util.Collection;
import java.util.Map;
import ${@responseType.@pkg}.${@responseType.@name};
$[for ${var} in ${@variables}]$[if ${var.@isBasicType}]$[else]import ${var.@pkg}.${var.@type};
$[end if]$[end for]
import com.voxlearning.utopia.service.spg.annotation.FlashUrl;

/**
 * ${@comment}
 */
@FlashUrl("${@url}")
public class ${@name}Request extends AbstractMessageBean implements Serializable
{
	private static final long serialVersionUID = 0L ;
	
	$[for ${var} in ${@variables}]/** ${var.@comment} */
	$[if ${var.@isArray}]public Collection<${var.@typeUpper}> ${var.@name};
	$[else]public ${var.@type} ${var.@name};
	$[end if]$[end for]
	
	/**
	 * 将请求过来的JSON字符串解析为类对象
	 * @param 请求过来的JSON字符串
	 * @return 解析好的对象
	 */
	@SuppressWarnings("unchecked")
	public static ${@name}Request parseRequest(String input)
	{
		${@name}Request req = JsonUtils.fromJson(input,${@name}Request.class);
		if(null == req){
			throw new NullPointerException();
		}
		return req;
	}
	
	/**
	 * 生成一个对应的返回类型对象
	 * @return 该类型消息对应的返回类型对象
	 */
	public static ${@responseType.@name} newResponse()
	{
		${@responseType.@name} response = new ${@responseType.@name}();
		return response;
	}
}