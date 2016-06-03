{
	"types":{
		$[for ${type} in ${@types}]"${type.@name}":"${type.@hash}",
		$[end for]
		"null":null
	},
	"messages":{
		$[for ${msg} in ${@messages}]"${msg.@name}":"${msg.@hash}",
		$[end for]
		"null":null
	}
}