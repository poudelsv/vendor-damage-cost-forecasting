-- PostgreSQL schema (ingest.py adapts types for the SQLite fallback).
CREATE TABLE IF NOT EXISTS vendors (vendor_id TEXT PRIMARY KEY, vendor_name TEXT, primary_process TEXT, contract_start DATE, stations INTEGER);
CREATE TABLE IF NOT EXISTS incidents (incident_id TEXT PRIMARY KEY, incident_date DATE, vendor_id TEXT REFERENCES vendors(vendor_id), process TEXT, damage_type TEXT, damage_cost_usd NUMERIC(10,2), severity TEXT);
CREATE TABLE IF NOT EXISTS damage_costs (incident_id TEXT REFERENCES incidents(incident_id), parts_usd NUMERIC(10,2), labour_usd NUMERIC(10,2), downtime_usd NUMERIC(10,2), total_usd NUMERIC(10,2));
CREATE TABLE IF NOT EXISTS audits (audit_id TEXT PRIMARY KEY, audit_date DATE, vendor_id TEXT REFERENCES vendors(vendor_id), process TEXT, vendor_reported_findings INTEGER, leader_findings INTEGER, discrepancy_type TEXT, repeat_operational_issue TEXT);
