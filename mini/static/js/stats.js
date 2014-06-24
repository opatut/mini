$(document).ready(function() {
    // $(".chart-container").kinetic();
    loadCommitActivity();
    loadContributions();
});

function loadCommitActivity() {
    var spinner = $("#chart-commit-activity").spinner();

    $.ajax({
        url: '/api/'+repository.slug+'/stats/commit-activity/', 
        dataType: 'json',
        success: function(data) {
            var insertions = [], deletions = [], commits = []; 
            $.each(data, function(key, value) {
                var date = parseDate(key);
                insertions.push({x: date, y: value.insertions});
                deletions.push({x: date, y: -value.deletions});
                commits.push({x: date, y: value.commits});
            });
            spinner.fadeOut(500, function() { spinner.hide(); });
            chartCommitActivity(insertions, deletions, commits);
        },
        error: function(jxs, textStatus, error) {
            alert(textStatus);
        }
    });
}

function loadContributions() {
    var spinner = $("#chart-contributions-lines, #chart-contributions-commits").spinner();
    $.ajax({
        url: '/api/'+repository.slug+'/stats/contributions/', 
        dataType: 'json',
        success: function(data) {
            var commits = [], lines = [];
            $.each(data, function(key, value) {
                commits.push([key, value.commits]);
                lines.push([key, value.lines]);
            });
            spinner.fadeOut(500, function() { spinner.hide(); });
            chartContributions(commits, lines);
        },
        error: function(jxs, textStatus, error) {
            alert(textStatus);
        }
    });
}


function chartCommitActivity(insertions, deletions, commits) {
    $('#chart-commit-activity').highcharts({
        chart: {
            type: 'spline',
            zoomType: 'x',
            marginTop: 50,
            alignTicks: true
        },
        plotOptions: {
            spline: {
                marker: {
                    enabled: false
                },
                lineWidth: 2,
                tooltip: {
                    valueSuffix: ' lines'
                },
            },
            column: {
                groupPadding: 0,
                pointPadding: 0,
                color: "rgba(100, 200, 255, 0.6)",
                tooltip: {
                    valueSuffix: ' commits'
                },
            }
        },
        legend: {
                align: 'left',
                verticalAlign: 'top',
                floating: true,
                x: 50,
                borderWidth: 0
            },
        colors: ["#00AA00", "#FF0000"],
        title: {
            text: '',
            visible: false
        },
        xAxis: {
            type: 'datetime',
            minRange: 14 * 24 * 3600000 // 14 days
        },
        yAxis: [{
            title: {
                text: 'Number of Lines'
            },
            // min: 0,
        },{
            title: {
                text: 'Commit count',
            },
            // linkedTo: 0,
            opposite: true
        }],
        series: [{
            type: 'column',
            name: 'Commits',
            yAxis: 1,
            data: commits,
        }, {
            name: 'Insertions',
            data: insertions,
        }, {
            name: 'Deletions',
            data: deletions,
        }]
    });
}

function chartContributions(commits, lines) {
    Highcharts.getOptions().colors = Highcharts.map(Highcharts.getOptions().colors, function(color) {
            return {
                radialGradient: { cx: 0.5, cy: 0.3, r: 0.7 },
                stops: [
                    [0, color],
                    [1, Highcharts.Color(color).brighten(-0.3).get('rgb')] // darken
                ]
            };
        });

    $('#chart-contributions-commits').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: 'Commits'
        },
        tooltip: {
            pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b> – {point.y}',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    }
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Commits',
            data: commits
        }]
    });

    $('#chart-contributions-lines').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        title: {
            text: 'Line changes'
        },
        tooltip: {
            pointFormat: '{point.name}: <b>{point.percentage:.1f}%</b>'
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b> – {point.y}',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    }
                }
            }
        },
        series: [{
            type: 'pie',
            name: 'Line changes',
            data: lines
        }]
    });
}