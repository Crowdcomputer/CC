function ShowModal(title, message) {
	$('#Modal .modal-header h3').text(title);
	$('#Modal .modal-body').html(message);
	$('#Modal').modal('show');
}


$(document).ready(function() {
	$('.js-code-example').click(function() {
		var title = 'CrowdMachine JavaScript Kit';
		var message = '<p>In order to have a possibility to send meta-data to crowdmachine through your website, please connect our JSKit:</p>';
		message += '<code>&lt;script src="http://goo.gl/hW97M"&gt;&lt;/script&gt;</code>';
		//message+='<img src="'+static+'img/js-example.png" />';
		message += '<p>Please connect JSKit <strong>after</strong> you connect the <a href="http://jquery.com/" target="_blank"><span class="label label-info">jQuery</span></a>:<br/> (if you do not, make sure you do)</p>';
		message += '<code>&lt;script src="http://code.jquery.com/jquery-latest.js"&gt;&lt;/script&gt;</code>';
		message += '<h5>Example of sending meta-data</h5><p> Create an array:</p>';
		message += '<code>var meta-data-s=new Array();</code>';
		message += '<p>Create an object containing meta-data:</p>';
		message += '<code>var meta-data = new Object();</code><br/>';
		message += '<code>meta-data.id = 1;</code><br/>';
		message += '<code>meta-data.url = "http://storage.com/1.png";</code><br/>';
		message += '<code>meta-data-s.push(meta-data);</code><br/>';
		message += '<p>Send meta-data to crowdmachine:</p>';
		message += '<code>CM_result(JSON.stringify(meta-data-s));</code>';
		message += '<hr>When CrowdMachine receives the meta-data, it thinks that task is completed, so send it only in the end of the task.';
		ShowModal(title, message);
	});
});

