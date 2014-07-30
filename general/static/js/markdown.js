$(document).ready(function() {
	function footerPlace() {
		if ($('#wrap .container').height() > $(window).height() - $('.navbar-inner').height() - $('footer').height() - 20)
			$('#wrap').css('margin-bottom', '0px');
		else
			$('#wrap').css('margin-bottom', '-80px');
	}
	footerPlace();
	$(window).resize(function() {
		footerPlace();
	});
});

