package ${@pkg};

import com.voxlearning.utopia.entity.flashmsg.AbstractMessageBean;
import com.a17zuoye.commons.lang.json.JsonUtils;

import java.io.Serializable;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Map;
$[for ${var} in ${@variables}]
$[if ${var.@isBasicType}] $[else]
import ${var.@pkg}.${var.@type};
$[end if]
$[end for]

/**
 * ${@comment}
 */
public class ${@name} extends AbstractMessageBean implements Serializable
{
	private static final long serialVersionUID = 0L ;
	
	/** 返回结果时表示是否操作成功 */
	public boolean success;
	$[for ${var} in ${@variables}]/** ${var.@comment} */
	$[if ${var.@isMap}]$[if ${var.@isArray}]public Map<${var.@keyTypeUpper}, List<${var.@typeUpper}>> ${var.@name};
	$[else]public Map<${var.@keyTypeUpper}, ${var.@typeUpper}> ${var.@name};
	$[end if]$[else]$[if ${var.@isArray}]public Collection<${var.@typeUpper}> ${var.@name};
	$[else]public ${var.@type} ${var.@name};
	$[end if]$[end if]$[end for]
	
	/**
	 * 将当前对象转换成返回需要的字符串
	 * @return 返回字符串，通常是JSON
	 */
	public String toResponse()
	{
		return JsonUtils.toJson(this);
	}
}