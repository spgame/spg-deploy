[
	$[for ${msg} in ${@messages}]"${msg.@url}":"${msg.@javaClass}",
	$[end for]
	"null":null
]