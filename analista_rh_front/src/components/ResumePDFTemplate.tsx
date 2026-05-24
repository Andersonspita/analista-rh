import React from 'react';
import { Document, Page, Text, View, StyleSheet, Font } from '@react-pdf/renderer';

// Font registration (optional, but good for explicit weights if using custom fonts. Times-Roman is built-in)
// Let's use the default Times-Roman

const styles = StyleSheet.create({
  page: {
    padding: 40,
    fontFamily: 'Times-Roman',
    backgroundColor: '#ffffff',
  },
  header: {
    textAlign: 'center',
    marginBottom: 20,
  },
  name: {
    color: '#003399',
    fontSize: 24,
    marginBottom: 8,
    fontFamily: 'Times-Bold',
  },
  contactInfo: {
    fontSize: 12,
    color: '#555555',
  },
  thickLine: {
    borderBottomWidth: 3,
    borderBottomColor: '#003399',
    marginBottom: 15,
  },
  section: {
    marginBottom: 15,
  },
  sectionTitle: {
    color: '#003399',
    fontSize: 14,
    fontFamily: 'Times-Bold',
    textTransform: 'uppercase',
    marginBottom: 6,
  },
  thinLine: {
    borderBottomWidth: 1,
    borderBottomColor: '#b3d1ff',
    marginBottom: 8,
  },
  paragraph: {
    fontSize: 12,
    lineHeight: 1.5,
    textAlign: 'justify',
    color: '#000000',
  },
  itemContainer: {
    marginBottom: 12,
  },
  itemHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'baseline',
  },
  itemTitle: {
    fontSize: 13,
    fontFamily: 'Times-Bold',
    color: '#000000',
  },
  itemDate: {
    fontSize: 12,
    color: '#666666',
    fontFamily: 'Times-Italic',
  },
  itemSubtitle: {
    color: '#003399',
    fontSize: 12,
    fontFamily: 'Times-Bold',
    textTransform: 'uppercase',
    marginTop: 2,
    marginBottom: 4,
  },
  itemDescription: {
    fontSize: 12,
    lineHeight: 1.5,
    textAlign: 'justify',
    color: '#000000',
  }
});

interface ResumePDFTemplateProps {
  data: any;
}

export const ResumePDFDocument: React.FC<ResumePDFTemplateProps> = ({ data }) => {
  if (!data) return null;

  return (
    <Document>
      <Page size="A4" style={styles.page}>
        
        {/* HEADER */}
        <View style={styles.header}>
          <Text style={styles.name}>{data.nome_completo}</Text>
          <Text style={styles.contactInfo}>
            {data.email} {data.telefone ? `- ${data.telefone}` : ''}
          </Text>
        </View>

        <View style={styles.thickLine} />

        {/* RESUMO PROFISSIONAL */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Resumo Profissional</Text>
          <View style={styles.thinLine} />
          <Text style={styles.paragraph}>{data.resumo_profissional}</Text>
        </View>

        {/* HABILIDADES TÉCNICAS */}
        {data.habilidades_tecnicas && data.habilidades_tecnicas.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Habilidades Técnicas</Text>
            <View style={styles.thinLine} />
            <Text style={styles.paragraph}>
              {data.habilidades_tecnicas.join(' • ')}
            </Text>
          </View>
        )}

        {/* EXPERIÊNCIA PROFISSIONAL */}
        {data.experiencias && data.experiencias.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Experiência Profissional</Text>
            <View style={styles.thinLine} />
            {data.experiencias.map((exp: any, index: number) => (
              <View key={index} style={styles.itemContainer} wrap={false}>
                <View style={styles.itemHeader}>
                  <Text style={styles.itemTitle}>{exp.cargo}</Text>
                  <Text style={styles.itemDate}>{exp.periodo}</Text>
                </View>
                <Text style={styles.itemSubtitle}>{exp.empresa}</Text>
                <Text style={styles.itemDescription}>{exp.descricao}</Text>
              </View>
            ))}
          </View>
        )}

        {/* FORMAÇÃO ACADÊMICA */}
        {data.formacao_academica && data.formacao_academica.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Formação Acadêmica</Text>
            <View style={styles.thinLine} />
            {data.formacao_academica.map((form: any, index: number) => (
              <View key={index} style={styles.itemContainer} wrap={false}>
                <View style={styles.itemHeader}>
                  <Text style={styles.itemTitle}>{form.curso}</Text>
                  <Text style={styles.itemDate}>{form.periodo}</Text>
                </View>
                <Text style={styles.itemSubtitle}>{form.instituicao}</Text>
              </View>
            ))}
          </View>
        )}

        {/* CURSOS / CERTIFICAÇÕES */}
        {data.cursos_certificacoes && data.cursos_certificacoes.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Cursos Complementares / Certificações</Text>
            <View style={styles.thinLine} />
            {data.cursos_certificacoes.map((curso: any, index: number) => (
              <View key={index} style={styles.itemContainer} wrap={false}>
                <View style={styles.itemHeader}>
                  <Text style={styles.itemTitle}>{curso.nome}</Text>
                  <Text style={styles.itemDate}>{curso.periodo || ''}</Text>
                </View>
                <Text style={styles.itemSubtitle}>{curso.instituicao}</Text>
              </View>
            ))}
          </View>
        )}

      </Page>
    </Document>
  );
};
