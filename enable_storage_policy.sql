-- ========================================================================
-- NEXUS GAMING ARENA - STORAGE ACCESS POLICY FOR SUPABASE
-- Run this in your Supabase SQL Editor (Takes 5 seconds):
-- 1. Open your Supabase Dashboard: https://supabase.com/dashboard
-- 2. Go to 'SQL Editor' in the left menu.
-- 3. Click 'New query', paste this whole script, and click 'Run'.
-- ========================================================================

-- Ensure the bucket exists and is public
INSERT INTO storage.buckets (id, name, public) 
VALUES ('nexus-arena', 'nexus-arena', true)
ON CONFLICT (id) DO UPDATE SET public = true;

-- Clean up any prior conflicting policies on this bucket
DROP POLICY IF EXISTS "Public Upload nexus-arena" ON storage.objects;
DROP POLICY IF EXISTS "Public Select nexus-arena" ON storage.objects;
DROP POLICY IF EXISTS "Public Update nexus-arena" ON storage.objects;

-- 1. Allow upload (INSERT) into nexus-arena bucket
CREATE POLICY "Public Upload nexus-arena" ON storage.objects 
FOR INSERT TO public WITH CHECK (bucket_id = 'nexus-arena');

-- 2. Allow reading/viewing (SELECT) files from nexus-arena bucket
CREATE POLICY "Public Select nexus-arena" ON storage.objects 
FOR SELECT TO public USING (bucket_id = 'nexus-arena');

-- 3. Allow updating (UPDATE) files in nexus-arena bucket
CREATE POLICY "Public Update nexus-arena" ON storage.objects 
FOR UPDATE TO public USING (bucket_id = 'nexus-arena');
