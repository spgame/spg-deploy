[
	$[for ${msg} in ${@messages}]"${msg.@url}":"${msg.@serverClass}",
	$[end for]
	"null":null
]