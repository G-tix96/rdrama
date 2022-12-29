function removeMod(e) {
	sendFormXHR(e,
		() => {
			e.target.parentElement.parentElement.remove();
		}
	)
}
