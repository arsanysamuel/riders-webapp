/* Global Variables */
const weekdays = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];

/* When the document is fully loaded */
$(document).ready(function() {

    /* ----------------------------------- Keyboard switch events -----------------------------------  */

    $(document).on("keypress", function(e) {
        var current_route = window.location.pathname

        // Preventing the default enter key behaviour (of submitting forms)
        if (e.which == 13) {
            switch(current_route) {
                case "/create":
                    e.preventDefault();
            }
        }

        if (e.which == 13 && $("#segment-input").is(":focus")) {  
            // adding new route segment
            addSeg();
            $("#segment-input").focus();
        } else if (e.which == 13 && $(".editItem").is(":focus")) {  
            // editing item
            const $focused = $(':focus');
            const segment = $focused.val()
            $focused.parent().replaceWith(`<span class="segment-name">${segment}</span><input class="segment-value" type="hidden" name="route[]" value="${segment}">`);
        }
    });


    /* ----------------------------------- Register Form -----------------------------------  */

    // Password matching
    $("#register-confirmation").on("change", function() {
        if ($(this).val() != $("#register-password").val()) {
            this.setCustomValidity("Password mismatch!");
        } else {
            this.setCustomValidity("");
        }
    });

    // Check for arabic characters in the arabic name field
    $("#arabic").on("change", function() {
        var arabic = /^[\u0600-\u06FF\s]+$/;  // regex for arabic unicode characters

        if (!arabic.test($(this).val())) {
            this.setCustomValidity("Name must be in arabic!");
        } else {
            this.setCustomValidity("");
        }
    });

    // Prevent the input of nonnumerical characters in numbers class
    $(".numbers").on("input", function() {
        $(this).val(function(i, v) {
            return v.replace(/[^0-9.]/g, '').replace(/(\..*)\./g, '$1');
        });
    });

    // AJAX: check for username duplicates
    $("#register-username").on("change", function() {
        let val = $(this).val()
        $.ajax({
            url: "/match-username",
            data: {
                input_username: val
            },
            type: "GET",
            datatype: "json"
        })

        // If the request succeeds, the response is passed to the function
        .done(function(response) {
            if (response["found"]) {
                $("#register-username")[0].setCustomValidity("Username already exists!");  // turns out it returns an array
            } else {
                $("#register-username")[0].setCustomValidity("");
            }
        })

        // Code to run if the request fails; the raw request and
        // status codes are passed to the function
        .fail(function(xhr, status, errorThrown) {
            alert("Sorry, there was a problem!");
            console.log("Error: " + errorThrown);
            console.log("Status: " + status);
            console.dir(xhr);
        });
    });

    // AJAX: check for email duplicates
    $("#register-email").on("change", function() {
        let val = $(this).val()
        $.ajax({
            url: "/match-email",
            data: {
                input_email: val
            },
            type: "GET",
            datatype: "json"
        })

        // If the request succeeds, the response is passed to the function
        .done(function(response) {
            if (response["found"]) {
                $("#register-email")[0].setCustomValidity("Email address already exists!");  // turns out it returns an array
            } else {
                $("#register-email")[0].setCustomValidity("");
            }
        })

        // Code to run if the request fails; the raw request and
        // status codes are passed to the function
        .fail(function(xhr, status, errorThrown) {
            alert("Sorry, there was a problem!");
            console.log("Error: " + errorThrown);
            console.log("Status: " + status);
            console.dir(xhr);
        });
    });

    // AJAX: check for phone number duplicates
    $("#register-phone").on("change", function() {
        let val = $(this).val()
        $.ajax({
            url: "/match-phone",
            data: {
                input_phone: val
            },
            type: "GET",
            datatype: "json"
        })

        // If the request succeeds, the response is passed to the function
        .done(function(response) {
            if (response["found"]) {
                $("#register-phone")[0].setCustomValidity("Phone number already exists!");  // turns out it returns an array
            } else {
                $("#register-phone")[0].setCustomValidity("");
            }
        })

        // Code to run if the request fails; the raw request and
        // status codes are passed to the function
        .fail(function(xhr, status, errorThrown) {
            alert("Sorry, there was a problem!");
            console.log("Error: " + errorThrown);
            console.log("Status: " + status);
            console.dir(xhr);
        });
    });

    /* ----------------------------------- Create Ride -----------------------------------  */

    // Get weekday of the date
    $("#ride-date").on("change", function() {
        let date = new Date($(this).val());
        weekday_i = date.getDay()
        $("#weekday-footnote").html("Weekday: " + weekdays[weekday_i]);
        $("#ride-weekday").val(weekday_i);
    });

    // Make sure moving_time is after assembly_time
    $("#assembly_time").on("change", function() {
        $("#moving_time").attr("min", $(this).val());
    });
    //$("#moving_time").on("change", function() {
    $("#moving_time").focusout(function() {
        if ($(this).val() < $("#assembly_time").val()) {
            this.setCustomValidity("Must be after the assembly time");
            this.reportValidity();
        } else {
            this.setCustomValidity("");
        }
    });

    // Make sure max-speed is more than min-speed
    $("#max-speed").on("change", function() {
        let min = Number($("#min-speed").val());
        let max = Number($("#max-speed").val());
        if (max < min) {
            this.setCustomValidity("Must be more than " + min);
        } else {
            this.setCustomValidity("");
        }
    });


    /* ----------------------------------- Create Ride: add route -----------------------------------  */
    var $route_placeholder = $("#route-placeholder");
    var $route_ul = $("<ul class='list-group'></ul>");

    // Create the action buttons for route segments
    const $remove = $('<button class="btn btn-sm route-control remove-segment" title="Remove" type="button"><i class="fa-solid fa-trash-can"></i></button>');
    const $edit = $('<button class="btn btn-sm route-control edit-segment" title="Edit" type="button"><i class="fa-solid fa-pen"></i></button>');
    const $up = $('<button class="btn btn-sm route-control up-segment" title="Move up" type="button"><i class="fa-solid fa-arrow-up"></i></button>');
    const $down = $('<button class="btn btn-sm route-control down-segment" title="Move down" type="button"><i class="fa-solid fa-arrow-down"></i></button>');
    const $segment_buttons_div = $('<div class="d-inline-flex ms-auto segment-btns"></div>');
    $segment_buttons_div.html([$down, $up, $edit, $remove]);
    $(".route-segment").append($segment_buttons_div.clone(true, true));

    // Remove button function
    $("body").on("click", "button.remove-segment", function() {  // using this method of selection to apply to the dynamically created elements
        $(this).parents(".list-group-item").remove();
        if (!$("#route-segment-list").length) {  // if the last item was removed
            $route_ul.replaceWith($route_placeholder);
        }
    });

    // Up button function
    $("body").on("click", "button.up-segment", function() {
        $(this).parents(".list-group-item").insertBefore($(this).parents(".list-group-item").prev());
    });

    // Down button function
    $("body").on("click", "button.down-segment", function() {
        $(this).parents(".list-group-item").insertAfter($(this).parents(".list-group-item").next());
    });

    // Edit button function
    $("body").on("click", "button.edit-segment", function() {
        const $item = $(this).parents(".route-segment").children(".segment-name");
        const $inputSpan = $("<span class='input-group editSpan'><input type='text' dir='auto' class='editItem form-control'><button class='btn btn-outline-success confirm-segment-edit' type='button'><i class='fa-solid fa-check'></i></button></span>");
        const $input = $inputSpan.children(".editItem");
        $input.val($item.html());
        $item.replaceWith($inputSpan);
        $input[0].select();  // select all text inside
    });

    // Confirm edit button function
    $("body").on("click", "button.confirm-segment-edit", function() {
        const $focused = $(':focus');
        const segment = $focused.siblings(".editItem").val()
        $focused.parent().replaceWith(`<span class="segment-name">${segment}</span><input class="segment-value" type="hidden" name="route[]" value="${segment}">`);
    });

    // Add road segments
    function addSeg() {
        const $segment_input = $("#segment-input");
        const segment = $segment_input.val()
        const $route_li = $("<li class='list-group-item' id='route-segment-list'></li>");
        const $segment_div = $("<div class='route-segment d-flex justify-content-center align-items-center'></div>");

        if (segment === "") {
            $segment_input[0].setCustomValidity("Blank input");
            $segment_input[0].reportValidity();
        } else {
            $segment_input[0].setCustomValidity("");
            if ($("#route-placeholder").length) {  // if the placeholder exists
                $route_placeholder.replaceWith($route_ul);
            } 

            // Add the segment
            $segment_div.html(`<span class="segment-name">${segment}</span><input class="segment-value" type="hidden" name="route[]" value="${segment}">`);
            $segment_div.append($segment_buttons_div.clone(true, true));
            $route_li.html($segment_div);
            $route_ul.append($route_li);
            $segment_input.val("");
        }
    }
    
    // Route adding event handlers
    $("#add-segment").on("click", addSeg);

    // Check if there is a route added
    $("#create-ride-form").on("submit", function(event) {
        if (!$("#route-segment-list").length) {
            alert("Route is blank, please add a route before creating the ride!");
            event.preventDefault();
        }
    });

    /* ----------------------------------- Join Ride -----------------------------------  */

    // Expand/Collapse icon
    $(".ride-item").on("click", function() {
        const icon = $(this).find(".collapse-icon").children()
        if (icon.hasClass("fa-chevron-down")) {
            icon.replaceWith($('<i class="fa-solid fa-chevron-up"></i>'))
        } else {
            icon.replaceWith($('<i class="fa-solid fa-chevron-down"></i>'))
        }
    });

    // Join button
    $("body").on("click", "button.join-btn", function() {
        const $join_btn = $(this)
        let id = $join_btn.parents(".ride-btns-div").siblings(".ride-id").val();

        $.ajax({
            url: "/rides/join",
            type: "POST",
            data: {
                ride_id: id
            },
            datatype: "json"
        })

        // If the request succeeds, the response is passed to the function
        .done(function(response) {
            // Add the user to the participants list
            const $ride_item = $join_btn.parents(".list-group-item")
            const $list = $ride_item.find(".participants-list");
            const $list_html = $('<div class="d-flex justify-content-center"><ol class="participants-list" dir="auto"></ol></div>');
            const $list_item = $(`<li>${response["participant"]}</li>`);

            if ($list.length) {
                $list.append($list_item);
            } else {
                $list_html.children(".participants-list").append($list_item);
                $ride_item.find(".participants-placeholder").replaceWith($list_html);
            }

            // Replace button
            $join_btn.replaceWith($('<button value="{{ ride["id"] }}" type="button" class="btn btn-secondary btn-lg leave-btn">Leave</button>'));
        })

        // Code to run if the request fails; the raw request and
        // status codes are passed to the function
        .fail(function(xhr, status, errorThrown) {
            alert("Sorry, there was a problem!");
            console.log("Error: " + errorThrown);
            console.log("Status: " + status);
            console.dir(xhr);
        });
    });

    // Leave button 
    $("body").on("click", "button.leave-btn", function() {
        const $leave_btn = $(this)
        let id = $(this).parents(".ride-btns-div").siblings(".ride-id").val();

        $.ajax({
            url: "/rides/leave",
            type: "POST",
            data: {
                ride_id: id
            },
            datatype: "json"
        })

        // If the request succeeds, the response is passed to the function
        .done(function(response) {
            // Remove the user from the participants list
            const $ride_item = $leave_btn.parents(".list-group-item");
            const $list = $ride_item.find(".participants-list");
            const $list_placeholder = $('<p class="participants-placeholder">No other participants yet.</p>');

            $list.children(`li:contains('${response["participant"]}')`).remove();

            if ($list.length) {
                $list.replaceWith($list_placeholder);
            }

            // if there's a new leader in responses
            if (response["new_lead"]) {
                if (response["leader"].length > 0){
                    // Add the new ride leader
                    $ride_item.find(".leader-p").html(`Leader: ${response["leader"]}`);
                } else {
                    console.log("cancel-ride")
                    // Cancel ride
                    const warning_modal = new bootstrap.Modal('#last-leave-warning', {keyboard: false});
                    warning_modal.show();
                    //$("#last-leave-warning").modal("show");
                    cancel_ride(id, $ride_item);
                    return; 
                }
            }

            // Replace button and remove cancel button
            $leave_btn.parents(".ride-btns-div").find(".cancel-btn").remove();
            $leave_btn.replaceWith($('<button value="{{ ride["id"] }}" type="button" class="btn btn-success btn-lg join-btn">Join</button>'));
        })

        // Code to run if the request fails; the raw request and
        // status codes are passed to the function
        .fail(function(xhr, status, errorThrown) {
            alert("Sorry, there was a problem!");
            console.log("Error: " + errorThrown);
            console.log("Status: " + status);
            console.dir(xhr);
        });
    });

    // Cancel button (for ride leader)
    $(".cancel-btn").on("click", function() {
        const $ride_item = $(this).parents(".list-group-item");
        let id = $ride_item.find(".ride-id").val();
        cancel_ride(id, $ride_item);
    });

    function cancel_ride(ride_id, $ride_item) {
        $.ajax({
            url: "/rides/cancel",
            type: "POST",
            data: {
                ride_id: ride_id
            },
            datatype: "json"
        })

        // If the request succeeds, the response is passed to the function
        .done(function(response) {
            // Remove ride-list item
            $ride_item.remove();

            // If last ride replace with placeholder
            if(!$(".list-group-item").length) {
                $("#rides-list-div").html('<h3 class="text-muted">Sorry, there are no upcoming rides currently. Check back later or <a href="/create">create</a> a new ride.</h3><br>');
            }
        })

        // Code to run if the request fails; the raw request and
        // status codes are passed to the function
        .fail(function(xhr, status, errorThrown) {
            alert("Sorry, there was a problem!");
            console.log("Error: " + errorThrown);
            console.log("Status: " + status);
            console.dir(xhr);
        });
    }

});

