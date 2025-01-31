"""update product summary functions to include descriptions

Revision ID: 002_update_product_summary
Revises: 54ce9cc70ef7
Create Date: 2024-01-31
"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '002_update_product_summary'
down_revision = '54ce9cc70ef7'
branch_labels = None
depends_on = None

def upgrade():
    # Drop existing trigger first
    op.execute("DROP TRIGGER IF EXISTS product_changes ON products;")
    
    # Drop existing functions
    op.execute("DROP FUNCTION IF EXISTS update_project_products_summary();")
    op.execute("DROP FUNCTION IF EXISTS rebuild_project_products_summary(uuid);")

    # Create updated trigger function
    op.execute("""
        CREATE OR REPLACE FUNCTION update_project_products_summary()
        RETURNS TRIGGER AS $$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                -- Add new product to summary
                UPDATE projects 
                SET products_summary = jsonb_set(
                    jsonb_set(
                        products_summary,
                        '{products}',
                        (products_summary->'products') || 
                        jsonb_build_object(
                            'id', NEW.id::text, 
                            'name', NEW.name,
                            'description', NEW.description
                        )::jsonb
                    ),
                    '{total_count}',
                    ((products_summary->>'total_count')::int + 1)::text::jsonb
                )
                WHERE id = NEW.project_id;
                RETURN NEW;
            ELSIF (TG_OP = 'UPDATE') THEN
                -- Update product name and description in summary if they changed
                IF OLD.name <> NEW.name OR OLD.description IS DISTINCT FROM NEW.description THEN
                    UPDATE projects 
                    SET products_summary = jsonb_set(
                        products_summary,
                        '{products}',
                        (
                            SELECT jsonb_agg(
                                CASE 
                                    WHEN (value->>'id')::uuid = NEW.id 
                                    THEN jsonb_build_object(
                                        'id', NEW.id::text, 
                                        'name', NEW.name,
                                        'description', NEW.description
                                    )
                                    ELSE value 
                                END
                            )
                            FROM jsonb_array_elements(products_summary->'products')
                        )
                    )
                    WHERE id = NEW.project_id;
                END IF;
                RETURN NEW;
            ELSIF (TG_OP = 'DELETE') THEN
                -- Remove product from summary
                UPDATE projects 
                SET products_summary = jsonb_set(
                    jsonb_set(
                        products_summary,
                        '{products}',
                        (
                            SELECT jsonb_agg(value)
                            FROM jsonb_array_elements(products_summary->'products')
                            WHERE (value->>'id')::uuid <> OLD.id
                        )
                    ),
                    '{total_count}',
                    ((products_summary->>'total_count')::int - 1)::text::jsonb
                )
                WHERE id = OLD.project_id;
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Create trigger
    op.execute("""
        CREATE TRIGGER product_changes
        AFTER INSERT OR UPDATE OR DELETE ON products
        FOR EACH ROW EXECUTE FUNCTION update_project_products_summary();
    """)

    # Create updated rebuild function
    op.execute("""
        CREATE OR REPLACE FUNCTION rebuild_project_products_summary(project_uuid uuid)
        RETURNS void AS $$
        BEGIN
            UPDATE projects
            SET products_summary = (
                SELECT jsonb_build_object(
                    'products', COALESCE(jsonb_agg(
                        jsonb_build_object(
                            'id', id::text, 
                            'name', name,
                            'description', description
                        )
                    ), '[]'::jsonb),
                    'total_count', COUNT(*)
                )
                FROM products
                WHERE project_id = project_uuid
            )
            WHERE id = project_uuid;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Rebuild summaries for all projects
    op.execute("""
        SELECT rebuild_project_products_summary(id) FROM projects;
    """)

def downgrade():
    # Drop trigger first
    op.execute("DROP TRIGGER IF EXISTS product_changes ON products;")
    
    # Drop functions
    op.execute("DROP FUNCTION IF EXISTS update_project_products_summary();")
    op.execute("DROP FUNCTION IF EXISTS rebuild_project_products_summary(uuid);")

    # Recreate original functions (without description)
    op.execute("""
        CREATE OR REPLACE FUNCTION update_project_products_summary()
        RETURNS TRIGGER AS $$
        BEGIN
            IF (TG_OP = 'INSERT') THEN
                UPDATE projects 
                SET products_summary = jsonb_set(
                    jsonb_set(
                        products_summary,
                        '{products}',
                        (products_summary->'products') || 
                        jsonb_build_object('id', NEW.id::text, 'name', NEW.name)::jsonb
                    ),
                    '{total_count}',
                    ((products_summary->>'total_count')::int + 1)::text::jsonb
                )
                WHERE id = NEW.project_id;
                RETURN NEW;
            ELSIF (TG_OP = 'UPDATE') THEN
                IF OLD.name <> NEW.name THEN
                    UPDATE projects 
                    SET products_summary = jsonb_set(
                        products_summary,
                        '{products}',
                        (
                            SELECT jsonb_agg(
                                CASE 
                                    WHEN (value->>'id')::uuid = NEW.id 
                                    THEN jsonb_build_object('id', NEW.id::text, 'name', NEW.name)
                                    ELSE value 
                                END
                            )
                            FROM jsonb_array_elements(products_summary->'products')
                        )
                    )
                    WHERE id = NEW.project_id;
                END IF;
                RETURN NEW;
            ELSIF (TG_OP = 'DELETE') THEN
                UPDATE projects 
                SET products_summary = jsonb_set(
                    jsonb_set(
                        products_summary,
                        '{products}',
                        (
                            SELECT jsonb_agg(value)
                            FROM jsonb_array_elements(products_summary->'products')
                            WHERE (value->>'id')::uuid <> OLD.id
                        )
                    ),
                    '{total_count}',
                    ((products_summary->>'total_count')::int - 1)::text::jsonb
                )
                WHERE id = OLD.project_id;
                RETURN OLD;
            END IF;
            RETURN NULL;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE TRIGGER product_changes
        AFTER INSERT OR UPDATE OR DELETE ON products
        FOR EACH ROW EXECUTE FUNCTION update_project_products_summary();
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION rebuild_project_products_summary(project_uuid uuid)
        RETURNS void AS $$
        BEGIN
            UPDATE projects
            SET products_summary = (
                SELECT jsonb_build_object(
                    'products', COALESCE(jsonb_agg(jsonb_build_object('id', id::text, 'name', name)), '[]'::jsonb),
                    'total_count', COUNT(*)
                )
                FROM products
                WHERE project_id = project_uuid
            )
            WHERE id = project_uuid;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # Rebuild summaries for all projects
    op.execute("""
        SELECT rebuild_project_products_summary(id) FROM projects;
    """) 