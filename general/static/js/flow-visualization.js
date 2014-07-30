$(document).ready(function() {
	function getTaskById(id) {
		for (var i = 0, ii = task_list.length; i < ii; i++) {
			if (task_list[i].id == id)
				return task_list[i];
		}
		return false;
	}

	function getColor(status) {
		if (status == 'ST')
			return "#0000aa";
		if (status == 'FN')
			return "#00aa00";
		if (status == 'PR')
			return "#F3DE6F";
			
	}

	if (task_list.length > 0) {
		//	var shapes_text = new Array();

		dragger = function() {
			// Original coords for main element
			this.ox = this.type == "ellipse" ? this.attr("cx") : this.attr("x");
			this.oy = this.type == "ellipse" ? this.attr("cy") : this.attr("y");
			if (this.type != "text")
				this.animate({
					"fill-opacity" : .2
				}, 500);

			// Original coords for pair element
			this.pair.ox = this.pair.type == "ellipse" ? this.pair.attr("cx") : this.pair.attr("x");
			this.pair.oy = this.pair.type == "ellipse" ? this.pair.attr("cy") : this.pair.attr("y");
			if (this.pair.type != "text")
				this.pair.animate({
					"fill-opacity" : .2
				}, 500);
		}, move = function(dx, dy) {
			// Move main element
			var att = this.type == "ellipse" ? {
				cx : this.ox + dx,
				cy : this.oy + dy
			} : {
				x : this.ox + dx,
				y : this.oy + dy
			};
			this.attr(att);

			// Move paired element
			att = this.pair.type == "ellipse" ? {
				cx : this.pair.ox + dx,
				cy : this.pair.oy + dy
			} : {
				x : this.pair.ox + dx,
				y : this.pair.oy + dy
			};
			this.pair.attr(att);

			// Move connections
			for ( i = connections.length; i--; ) {
				r.connection(connections[i]);
			}
			r.safari();
		}, up = function() {
			// Fade original element on mouse up
			if (this.type != "text")
				this.animate({
					"fill-opacity" : 0.2
				}, 500);

			// Fade paired element on mouse up
			if (this.pair.type != "text")
				this.pair.animate({
					"fill-opacity" : 0.2
				}, 500);
		}
		var r = Raphael("holder", 1000, 250);
		var connections = [];
		for (var i = 0, ii = task_list.length; i < ii; i++) {
			var color = getColor(task_list[i].status);
			task_list[i].shape_rect = r.rect(50 + i * 100, 50 + i * 25, 70, 40, 5);
			task_list[i].shape_text = r.text(50 + i * 100 + 35, 50 + i * 25 + 20, task_list[i].title);
			task_list[i].shape_rect.attr({
				fill : color,
				stroke : color,
				"fill-opacity" : 0.2,
				"stroke-width" : 2,
				cursor : "move"
			});
			tempS = task_list[i].shape_rect;
			tempT = task_list[i].shape_text;

			// Make all the shapes and texts dragable
			task_list[i].shape_rect.drag(move, dragger, up);
			task_list[i].shape_text.drag(move, dragger, up);

			// Associate the elements
			tempS.pair = tempT;
			tempT.pair = tempS;

		}
		for (var i = 0, ii = task_list.length; i < ii; i++) {
			for (var j = 0, jj = task_list[i].inputs.length; j < jj; j++) {
				connections.push(r.connection(getTaskById(task_list[i].inputs[j]).shape_rect, task_list[i].shape_rect, "#bbb"));
			}
		}
	}

});
