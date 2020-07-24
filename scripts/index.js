const channelID = "UC5UAwBUum7CPN5buc-_N1Fw"

//if the following max videos size is changed then also create more carousal items in the html page 
const maxVideos = 4

//the following API_key is linked with my account but set as public api key
const API_key = "AIzaSyA62eqDWrTX1SSnzYcrcwMwIqb8HQYUcZ0"

$(document).ready(function () {
    $.get("https://www.googleapis.com/youtube/v3/channels", {
            part: "contentDetails",
            id: channelID,
            key: API_key
        },

        function (data) {
            $.each(data.items, function (i, item) {
                console.log(item)
                const pid = item.contentDetails.relatedPlaylists.uploads
                getVids(pid)
            })
        }
    )

    function getVids(pid) {
        $.get("https://www.googleapis.com/youtube/v3/playlistItems", {
                part: "snippet",
                maxResults: maxVideos,
                playlistId: pid,
                key: API_key
            },

            function (data) {
                //the following variable will be used for displaying the content on the page
                //the following output variable will contain the list items which will be inserted into the unordered list
                const videoLinks = []
                var currentVideoLink = ''
                $.each(data.items, function (i, item) {
                    vidId = item.snippet.resourceId.videoId;
                    currentVideoLink = 'https://www.youtube.com/embed/' + vidId;
                    videoLinks.push(currentVideoLink)
                })

                $(".first-video").attr('src', videoLinks[0]);
                $(".second-video").attr('src', videoLinks[1]);
                $(".third-video").attr('src', videoLinks[2]);
                $(".fourth-video").attr('src', videoLinks[3]);
            }
        )
    }
});
