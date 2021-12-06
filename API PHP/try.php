<?php
    $authorize_url = "https://account.withings.com/oauth2_user/authorize2";
    $token_url = "https://wbsapi.withings.net/v2/oauth2";
    $callback_uri = "https://hooks.zapier.com/hooks/catch/11269009/bdt08t3/";
    $api_url = "https://wbsapi.withings.net/sleep";
    $client_id = "156a17f1c19805f39cd29194733717a4a0a8b254d550ae162f01a386618ad53c";
    $client_secret = "89553a120b09f7518b6f6c18f63bd2fdc254dbc8cfbc9c746b603660b8000d89";


if ($_GET["code"]) {
        $access_token = getAccessToken($_GET["code"]);
       echo 'access_token = '.$access_token.'<br />';
        $resource = getWeight($access_token);
       echo 'Gewicht = '.$resource;
    } 
    else {
        getAuthorizationCode();
    }



function getAuthorizationCode() {
        global $authorize_url, $client_id, $callback_uri;
        $authorization_redirect_url = $authorize_url . "?response_type=code&client_id=" . $client_id . "&redirect_uri=" . $callback_uri . "&scope=user.metrics&state=test";
        header("Location: " . $authorization_redirect_url);
    }



function getAccessToken($authorization_code) {
        global $token_url, $client_id, $client_secret, $callback_uri;
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $token_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([ 
            'action' => 'requesttoken',
            'grant_type' => 'authorization_code',
            'client_id' => $client_id,
            'client_secret' => $client_secret,
            'code' => $authorization_code,
            'redirect_uri' => $callback_uri
        ]));
        $rsp = curl_exec($ch);
        curl_close($ch);
        $response = json_decode($rsp);
        var_dump($rsp);
        return $response->body->access_token;
    }


function getWeight($access_token) {
        global $api_url;
        $ch = curl_init();
        curl_setopt($ch, CURLOPT_URL, $api_url);
        curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);
        curl_setopt($ch, CURLOPT_HTTPHEADER, [
            'Authorization: Bearer '.$access_token
        ]);

        curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query([ 
            'action' => 'getmeas',
            'meastypes' => '1',
            'startdate' => '1623110400',
            'enddate' => '1623196799'
        ]));

        $rsp1 = curl_exec($ch);
        curl_close($ch);
        $response = json_decode($rsp1);
        var_dump($rsp1);
        return $response ->body->measuregrps[0]->measures[0]->value;
    }
?>