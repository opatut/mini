$(document).ready(function() {
    loadNetwork();
});

var commits;

var conf = {
    xSep: 22,
    ySep: 22,
    padding: 11,
    headline: 20,
    marginBottom: 30
};

function loadNetwork() {
    var spinner = $("#chart-commit-activity").spinner();

    $.ajax({
        url: '/api/'+repository.slug+'/stats/network/', 
        dataType: 'json',
        success: function(data) {
            spinner.fadeOut(500, function() { spinner.hide(); });
            commits = data.commits;
            chartNetwork();            
        },
        error: function(jxs, textStatus, error) {
            alert(textStatus);
        }
    });
}

var colors = [
    'black', 'orange', 'green', 'magenta', 'cyan', 'red', 'blue', 'yellow'
];

////////////////////////////////////////////////////////////////////////////////

function Arrow(from, to, type) {
    this.from = from;
    this.to = to;
    // generate type
    this.type = type || "ziczac";
}

Arrow.prototype.draw = function() {
    var context = this.from.network.context;

    // get positions
    var p = this.from.getPosition();
    var q = this.to.getPosition();

    // get and apply lane color
    var color = (p.y > q.y ? this.from : this.to).getColor();
    context.strokeStyle = color;
    context.fillStyle = color;
    context.lineWidth = 2;

    context.beginPath();

    context.moveTo(p.x, p.y);
    if(this.type == "normal") {
        if(p.y < q.y) {
            context.lineTo(p.x + 10, q.y);
        } else {
            context.lineTo(q.x - 10, p.y);
        }
        context.lineTo(q.x, q.y);
    } else if(this.type == "ziczac") {
        if(p.y < q.y) {
            // zic-zac arrow
            if(this.to.getParents().indexOf(this.from) != 0) {
                context.lineTo(p.x, q.y - 10);
                context.lineTo(q.x-10, q.y - 10);
            } else {
                context.lineTo(p.x + 10, q.y);
            }
        } else if(p.y > q.y) {
            if(this.from.getChildren().indexOf(this.to) != 0) {
                context.lineTo(p.x+10, p.y-10);
                context.lineTo(q.x-10, p.y-10);
            } else {
                context.lineTo(q.x - 10, p.y);
            }
        }
        context.lineTo(q.x, q.y);
    } else if(this.type == "curve") {
        var dx = (q.x - p.x) * 0.5;
        context.bezierCurveTo(p.x+dx, p.y, q.x-dx, q.y, q.x, q.y);
    } else if(this.type == "aligncurve") {
        if(p.y < q.y) {
            context.bezierCurveTo(p.x+conf.xSep/2, p.y, p.x+conf.xSep/2, q.y, p.x+conf.xSep, q.y);
            context.lineTo(q.x, q.y);
        } else {
            context.lineTo(q.x-conf.xSep, p.y);
            context.bezierCurveTo(q.x-conf.xSep/2, p.y, q.x-conf.xSep/2, q.y, q.x, q.y);
        }
    } else { // normal
        context.lineTo(q.x, q.y);
    }

    context.stroke();
};

////////////////////////////////////////////////////////////////////////////////

function Label(commit, text) {
    this.commit = commit;
    this.text = text;
}

Label.prototype.draw = function() {
    var context = this.commit.network.context;
    var p = this.commit.getPosition();

    context.save();
    context.translate(p.x, p.y + 5);

    var metrics = context.measureText(this.text);
    var w = 8;
    var h = metrics.width + 2 * w;

    context.beginPath();
    context.moveTo(0, 0);
    context.lineTo(w, w);
    context.lineTo(w, h);
    context.lineTo(-w, h);
    context.lineTo(-w, w);
    context.lineTo(0, 0);

    context.fillStyle = 'rgba(0, 0, 0, 0.8)';
    context.fill();

    context.translate(3, h - 5);
    context.rotate(-Math.PI / 2);
    context.fillStyle = 'white';
    context.fillText(this.text, 0, 0);

    context.restore();
};

////////////////////////////////////////////////////////////////////////////////

function Commit(network, data) {
    this.network = network;
    this.hexsha = data.hexsha;
    this.author = data.author;
    this.message = data.message;
    this.x = data.x;
    this.y = data.y;
    this.children_ids = data.children;
    this.parents_ids = data.parents;
    this.branches = data.branches;
    this.tags = data.tags;
    this.hover = false;
    this.active = false;
}

Commit.prototype.getLabel = function() {
    var branches = this.branches.join(", ");
    var tags = this.tags.join(", ");
    var label = branches; 
    if(label && tags) label += ", ";
    label += tags;
    return label;
};

Commit.prototype.getChildren = function() {
    var children = [];
    var commit = this;
    $.each(this.children_ids, function(_, id) {
        children.push(commit.network.commits[id]);
    });
    return children;
}

Commit.prototype.getParents = function() {
    var parents = [];
    var commit = this;
    $.each(this.parents_ids, function(_, id) {
        parents.push(commit.network.commits[id]);
    });
    return parents;
}

Commit.prototype.hasSameLaneParent = function() {
    return !!$.grep(this.getParents(), function(parent) {
        return parent.y == this.y;
    }, this);
};

Commit.prototype.createArrows = function() {
    var commit = this;
    // $.each(this.getChildren(), function(index, child) {
    //     var arrow = new Arrow(commit, child, index == 0 ? "normal" : "ziczac");
    //     commit.network.addArrow(arrow);
    // });
    $.each(this.getParents(), function(index, parent) {
        var arrow = new Arrow(parent, commit);
        commit.network.addArrow(arrow);
    });
};

Commit.prototype.createLabels = function() {
    var label = this.getLabel();
    if(!label) return;
    this.network.addLabel(new Label(this, label));
};

Commit.prototype.draw = function() {
    var context = this.network.context;
    var p = this.getPosition();
    var is_merge = (this.parents_ids.length == 2);
    var r = (this.hover ? 6 : 4) - (is_merge ? 1 : 0);

    context.beginPath();
    context.arc(p.x, p.y, r, 0, 2 * Math.PI, false);
    context.fillStyle = is_merge ? "white" : this.getColor();
    context.strokeStyle = is_merge || this.active ? this.getColor() : "white";
    context.lineWidth = 2;
    context.fill();
    context.stroke();
};

Commit.prototype.getColor = function() {
    return colors[this.y % colors.length];
}

Commit.prototype.getPosition = function() {
    return {
        x: (this.network.commits.length - this.x - 1) * conf.xSep + conf.padding, 
        y: this.y * conf.ySep + conf.padding + conf.headline * 2
    };
}

////////////////////////////////////////////////////////////////////////////////

function Network(container_id) {
    this.commits = [];
    this.arrows = [];
    this.labels = [];
}

Network.prototype.setupContext = function(container_id) {
    this.container = $("#network-graph-container");
    this.container.kinetic();
    var pw = this.container.width();

    this.canvas = this.container.find("canvas");
    this.context = this.canvas.get(0).getContext("2d");

    var maxY = 0;
    $.each(this.commits, function(_, commit) {
        if(commit.y > maxY) maxY = commit.y;
    });

    this.width = Math.max(this.container.width(), (commits.length - 1) * conf.xSep + 2 * conf.padding);
    this.height = maxY * conf.ySep + 2 * conf.padding + conf.headline * 2 + conf.marginBottom;

    this.canvas
        .attr("width", this.width)
        .attr("height", this.height)
        .css("width", this.width + "px")
        .css("height", this.height + "px");

    var network = this;
    this.canvas.mousemove(function(e) {
        var c = network.getCommitAtMouse(e);
        $.each(network.commits, function(_, commit) {
            commit.hover = (c == commit);
        });
        network.container.css("cursor", c ? "pointer" : "move");
        network.draw();

        var overlay = $("#network-commit-details");
        if(c) {
            overlay
                .fadeIn(100)
                .css("left", e.pageX)
                .css("top", e.pageY + 30);
            overlay.find(".author").text(c.author);
            overlay.find(".hexsha code").text(c.hexsha.substring(0, 8));
            overlay.find(".message").text(c.message);
        } else {
            $("#network-commit-details").fadeOut(100);
        }
    }).click(function(e) {
        var c = network.getCommitAtMouse(e);
        $.each(network.commits, function(_, commit) {
            commit.active = (c == commit);
        });
    });
};

Network.prototype.getCommitAtMouse = function(e) {
    var offset = this.canvas.offset();
    return this.getCommitAt(e.pageX - offset.left, e.pageY - offset.top);
}

Network.prototype.addCommits = function(commits) {
    var network = this;
    $.each(commits, function(_, data) {
        network.addCommit(new Commit(network, data));
    });

    $.each(this.commits, function(_, commit) {
        commit.createArrows();
        commit.createLabels();
    });
};

Network.prototype.addCommit = function(commit) {
    this.commits.push(commit);
};

Network.prototype.addArrow = function(arrow) {
    this.arrows.push(arrow);
    arrow.network = this;
};

Network.prototype.addLabel = function(label) {
    this.labels.push(label);
    label.network = this;
};

Network.prototype.draw = function() {
    var context = this.context;

    // clear canvas
    context.save();
    context.setTransform(1, 0, 0, 1, 0, 0);
    context.clearRect(0, 0, this.width, this.height);
    context.restore();

    // draw objects
    $.each(this.arrows, function(_, arrow) {
        arrow.draw();
    });
    $.each(this.commits, function(_, commit) {
        commit.draw();
    });
    $.each(this.labels, function(_, label) {
        label.draw();
    });

    // draw headline
    context.beginPath();
    context.rect(2, 2, this.width - 4, conf.headline - 2);
    context.fillStyle = "#181818";
    context.fill();

    context.beginPath();
    context.rect(2, conf.headline, this.width - 4, conf.headline - 2);
    context.fillStyle = "#303030";
    context.fill();
};

Network.prototype.getCommitAt = function(x, y, radius) {
    var close = $.grep(this.commits, function(commit) {
        var p = commit.getPosition();
        var dx = p.x - x;
        var dy = p.y - y;
        return Math.sqrt(dx * dx + dy * dy) < (radius || 8);
    });
    return close.length ? close[0] : null;
};

////////////////////////////////////////////////////////////////////////////////

function chartNetwork() {
    var network = new Network("network-graph-container");
    network.addCommits(commits);
    network.setupContext();
    network.draw();
}
