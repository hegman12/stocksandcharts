var amc1 = null;
var amc2 = 0;
var scheme_cat_id = null;
var schemeNavId1 = null;
var schemeNavName1 = ""
var schemeNavId2 = 0;
var schemeNavName2 = "";
var numDays = 360;
margin = {
    top: 40,
    bottom: 60,
    left: 30,
    right: 30
}
var svg1Width = d3.select('#graphOne').style("width").replace("px", "");
var svg1Height = d3.select('#graphOne').style("height").replace("px", "");
var graphOne = d3.select('#graphOne').append("g").attr("height", svg1Height - margin.top - margin.bottom).attr("width", svg1Width - margin.left - margin.right).attr("transform", "translate(" + margin.left + "," + margin.top + ")");
const options = d3.select('#graphOne').append("g").attr("width", svg1Width).attr("height", 30);
options.append("text").attr("x", 40).attr("y", 15).html("1month").on("click", function() {
    numDays = 30;
    options.selectAll("text").attr("class", "time-buttons");
    d3.select(this).classed("time-buttons-selected", true)
    call();
}).attr("class", "time-buttons");
options.append("text").attr("x", 140).attr("y", 15).html("3months").on("click", function() {
    numDays = 90;
    options.selectAll("text").attr("class", "time-buttons");
    d3.select(this).classed("time-buttons-selected", true)
    call();
}).attr("class", "time-buttons");
options.append("text").attr("x", 240).attr("y", 15).html("6months").on("click", function() {
    numDays = 180;
    options.selectAll("text").attr("class", "time-buttons");
    d3.select(this).classed("time-buttons-selected", true)
    call();
}).attr("class", "time-buttons");
options.append("text").attr("x", 340).attr("y", 15).html("1year").on("click", function() {
    numDays = 365;
    options.selectAll("text").attr("class", "time-buttons");
    d3.select(this).classed("time-buttons-selected", true)
    call();
}).attr("class", "time-buttons-selected");
options.append("text").attr("x", 440).attr("y", 15).html("2year").on("click", function() {
    numDays = 720;
    options.selectAll("text").attr("class", "time-buttons");
    d3.select(this).classed("time-buttons-selected", true)
    call();
}).attr("class", "time-buttons");
options.append("text").attr("x", 540).attr("y", 15).html("3year").on("click", function() {
    numDays = 1200;
    options.selectAll("text").attr("class", "time-buttons");
    d3.select(this).classed("time-buttons-selected", true)
    call();
}).attr("class", "time-buttons");
options.append("text").attr("x", 640).attr("y", 15).html("max").on("click", function() {
    numDays = 1700;
    options.selectAll("text").attr("class", "time-buttons");
    d3.select(this).classed("time-buttons-selected", true)
    call();
}).attr("class", "time-buttons");

function setAMC(id, value, o) {
    d3.selectAll("#schemeCategorySelection div label").classed("tagSelected", false);
    d3.selectAll("#schemeNavSelection").style("visibility", "hidden");
    d3.selectAll("#g1").style("visibility", "hidden");
    schemeNavId1 = null;
    schemeNavId2 = 0;
    if (id === "amc1") {
        amc1 = value;
    } else {
        amc2 = value;
    }
    d3.select("#" + id).text(o.text)
    getSchemeCategory('#schemeCategorySelection')
}

function getSchemeCategory(id) {
    if (amc1 != null) {
        var url = "/mutualfunds/schemeCat/" + amc1 + "/" + amc2;
        //var url = "/category/3266" + "/" + mode + end_url;
        d3.json(url, {
            headers: {
                "Authorization": "Basic " + token
            }
        }).then(function(data) {
            d3.select(id).style("visibility", "visible")
            updateSchemeCategory(id, data)
        }).catch(function(error) {
            if (error) {
                window.location.href = "/"
            }
        })
    }
}

function updateSchemeCategory(id, data) {
    var tags = d3.selectAll(id).selectAll("div").data(data, function(d) {
        return d.scheme_cat_id;
    })
    tags.exit().remove()
    tags.enter().append('div').attr("class", "tag").attr("id", function(d) {
            return "d" + d.scheme_cat_id
        }).append("label").attr("id", function(d) {
            return "l" + d.scheme_cat_id
        }).attr("tabIndex", "0").html(function(d) {
            return d.scheme_cat_short_name
        }).on("click", schemeCategoryClick).on("focus", function(d) {
            currentObject = this;
        })
        //refresh();
}

function schemeCategoryClick(d, i) {
    d3.selectAll("#schemeCategorySelection div label").classed("tagSelected", false);
    d3.select(document.activeElement).classed("tagSelected", true);
    d3.selectAll("#g1").style("visibility", "hidden");
    schemeNavId1 = null;
    schemeNavId2 = 0;
    scheme_cat_id = d.scheme_cat_id
    getSchemeNav("#schemeNavSelection");
};

function getSchemeNav(id) {
    if (amc1 != null) {
        var url = "/mutualfunds/schemeNav/" + amc1 + "/" + amc2 + "/" + scheme_cat_id;
        //var url = "/category/3266" + "/" + mode + end_url;
        d3.json(url, {
            headers: {
                "Authorization": "Basic " + token
            }
        }).then(function(data) {
            d3.select(id).style("visibility", "visible")
            updateSchemeNav(data)
        }).catch(function(error) {
            console.log(error)
            if (error) {
                //window.location.href = "/"
            }
        })
    }
}

function updateNavOptions(data, id) {
    var tags = d3.selectAll(id).selectAll("div").data(data, function(d) {
        return d.code;
    })
    tags.exit().remove()
    tags.enter().append('div').attr("class", "tag").attr("id", function(d) {
        return "d" + d.code
    }).append("label").attr("id", function(d) {
        return id + d.code
    }).attr("tabIndex", "0").html(function(d) {
        return d.scheme_nav_name
    }).on("click", schemeNavClick).on("focus", function(d) {
        currentObject = this;
    })
}

function updateSchemeNav(data) {
    amc1_data = data.filter(function(d) {
        return d.amc == amc1;
    })
    updateNavOptions(amc1_data, "#amc1s")
    amc2_data = data.filter(function(d) {
        return d.amc == amc2;
    })
    updateNavOptions(amc2_data, "#amc2s")
        //refresh();
}

function call() {
    var url = "/mutualfunds/performance/" + schemeNavId1 + "/" + schemeNavId2 + "/" + numDays;
    //var url = "/category/3266" + "/" + mode + end_url;
    d3.json(url, {
        headers: {
            "Authorization": "Basic " + token
        }
    }).then(function(data) {
        d3.select("#g1").style("visibility", "visible")
        render(data)
    }).catch(function(error) {
        if (error) {
            //window.location.href = "/"
        }
    })
}

function schemeNavClick(d, i) {
    id = document.activeElement.id
    if (id.startsWith("#amc2s")) {
        d3.selectAll("#schemeNavSelection #amc2s label").classed("tagSelected", false);
        d3.select(document.activeElement).classed("tagSelected", true);
        schemeNavId2 = d.code;
        schemeNavName2 = d.scheme_nav_name
    } else {
        d3.selectAll("#schemeNavSelection #amc1s label").classed("tagSelected", false);
        d3.select(document.activeElement).classed("tagSelected", true);
        schemeNavId1 = d.code;
        schemeNavName1 = d.scheme_nav_name
    }

    if (amc2 == 0 && schemeNavId1 != null) {
        call()
    } else if (amc2 != 0 && schemeNavId1 != null && schemeNavId2 != 0) {
        call()
    } else {

    }
};

function normalize(data) {
    d = []
    d[0] = 0
    var val;
    var denominator = data[0].nav_value
    var counter = 1;
    if (denominator == 0) {
        for (i = 1; i < data.length; i++) {
            if (data[i].nav_value != 0) {
                break;
            }
            d[counter] = 0;
            counter = counter + 1;
        }
    }
    for (i = counter; i < data.length; i++) {
        val = ((data[i].nav_value - data[counter].nav_value) / data[counter].nav_value) * 100
        if (val === -100) {
            d[i] = d[i - 1]
        } else if (!isFinite(val)) {
            d[i] = 0;
        } else {
            d[i] = val;
        }
    }
    return d
}

function addLegend(id, color, ty, name) {
    d3.select("#" + id).remove();
    var legend = d3.select('#graphOne').append("g").attr("id", id).attr("height", 20).attr("width", 20).attr("transform", "translate(0," + ty + ")");
    legend.append("line").attr("x1", margin.left).attr("y1", 10).attr("x2", margin.left + 100).attr("y2", 10).attr("strok-width", "5px").attr("stroke", color);
    legend.append("text").attr("y", 10).attr("x", margin.left + 100 + 5).html(name) //.attr("transform", "translate(" + margin.left + 100 + 20 + "," + ty + ")")
        //legend;
}

function render(data) {
    if (amc2 != 0) {
        scheme1_data = normalize(data[0])
        scheme2_data = normalize(data[1])
        scheme1_max = d3.max(scheme1_data)
        scheme1_min = d3.min(scheme1_data)
        scheme2_max = d3.max(scheme2_data)
        scheme2_min = d3.min(scheme2_data)
        if (scheme2_max > scheme1_max) {
            var max = scheme2_max
        } else {
            var max = scheme1_max
        }
        if (scheme2_min > scheme1_min) {
            var min = scheme1_min
        } else {
            var min = scheme2_min
        }

        render_price(scheme1_data, max, min, true, "red")
        addLegend("l1", "red", (svg1Height - 50), schemeNavName1)
        render_price(scheme2_data, max, min, false, "blue")
        addLegend("l2", "blue", (svg1Height - 30), schemeNavName2)

    } else {
        scheme1_data = normalize(data[0])
        scheme1_max = d3.max(scheme1_data)
        scheme1_min = d3.min(scheme1_data)
        render_price(scheme1_data, scheme1_max, scheme1_min, true, "red")
        d3.select("#l2").remove();
        addLegend("l1", "red", (svg1Height - 50), schemeNavName1)
    }
}

function getMinDate() {
    var fromDt = new Date();
    fromDt.setDate(fromDt.getDate() - numDays);
    return fromDt
}
var linspace = function(start, stop, num_samples) {
    var off = ((stop - start) / (num_samples - 1))
    return d3.range(0, num_samples)
        .map(function(n) {
            return Math.floor(n * off);
        });
};

function render_price(data, max, min, remove, color) {
    var width = Math.floor(svg1Width - margin.left - margin.right);
    var height = Math.floor(svg1Height - margin.top - margin.bottom);
    var scaleY = d3.scaleLinear().domain([min, max]).range([height, 0]);
    var scaleX = d3.scaleLinear().domain([0, data.length]).range([0, width]);
    var line = d3.line()
        .x(function(d, i) {
            return scaleX(i);
        })
        .y(function(d) {
            //console.log("for y i: " + i + ", d:" + Math.floor(yScale(d.y1)));
            return scaleY(d);
        }).curve(d3.curveBasis);
    if (remove) {
        graphOne.selectAll("path").remove();
        graphOne.selectAll("#bAxis").remove();
        graphOne.selectAll("#rAxis").remove();
    }
    //var lines = timelineChart();
    //svg.datum(data.map(d => d.y1)).call(lines).attr("stroke", "black").attr("stroke-width", "2px").attr("fill", "none");;
    graphOne.append("path").attr("d", line(data)).attr("stroke", color).attr("stroke-width", "2px").attr("fill", "none");

    graphOne.append("g").attr("id", "rAxis").call(d3.axisLeft(scaleY).tickFormat(function(d, i) {
        return d;
    }));
    scale = d3.scaleTime().domain([getMinDate(), new Date()]).range([0, width])
    graphOne.append("g").attr("id", "bAxis").call(d3.axisTop(scale)).attr("transform", "translate(0," + height + ")");

}