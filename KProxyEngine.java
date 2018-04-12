package com.osrpey.kproxy;

import com.google.api.gax.paging.Page;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import io.undertow.Undertow;
import io.undertow.predicate.Predicates;
import io.undertow.server.HttpHandler;
import io.undertow.server.HttpServerExchange;
import io.undertow.server.handlers.proxy.ProxyHandler;
import io.undertow.server.handlers.encoding.ContentEncodingRepository;
import io.undertow.server.handlers.encoding.EncodingHandler;
import io.undertow.server.handlers.encoding.GzipEncodingProvider;
import io.undertow.util.Headers;
import io.undertow.util.HttpString;
import io.undertow.util.Methods.*;
import java.nio.channels.Channels;
import com.fasterxml.jackson.databind.ObjectMapper;

public class KProxyEngine {

    public static void main(String[] args){
        System.out.println("start the kproxy engine....");
        BigQueryClient bqc = new BigQueryClient

    }   
}
